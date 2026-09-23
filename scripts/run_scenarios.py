#!/usr/bin/env python3
"""
run_scenarios.py: Number Pii Toolkit Scenario Evals

Measures whether the toolkit helps or hinders real coding agents. Each scenario
in evals/scenarios/*.toml gives an agent a natural request inside a scaffolded
fixture project (evals/scenarios/fixture/), then scores the resulting git state
objectively: tests and hidden completion tests, files touched outside scope,
dash-only churn, handover behaviour, doc discovery, main-branch safety, and
merge conflicts between two agents working in parallel. No LLM judge.

Every run happens in a fresh temp directory with a local bare `origin` whose
main branch rejects pushes. The toolkit under test is copied into the project
as a gitignored `organisation/` folder, exactly as consumers use it.

Usage:
    python3 scripts/run_scenarios.py --list
    python3 scripts/run_scenarios.py --smoke                      # default set, both runners
    python3 scripts/run_scenarios.py --all --repeat 3 --runner codex
    python3 scripts/run_scenarios.py --scenario bug_fix --toolkit-ref v3.19.1
    python3 scripts/run_scenarios.py --smoke --scorecard evals/scorecards/3.19.1.json
    python3 scripts/run_scenarios.py --setup-only doc_discovery   # build a workspace, no agent

Raw transcripts and per-run scores go to evals/results/ (gitignored).
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import agents  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SCEN_DIR = REPO_ROOT / "evals" / "scenarios"
FIXTURE = SCEN_DIR / "fixture"
RESULTS_DIR = REPO_ROOT / "evals" / "results"
PROJECT_NAME = "Bookings"
SEED_DATE = "2026-09-01"

# Paths every scenario may touch: handover records and decision records.
DEFAULT_ALLOWED = ["doc/handover/**", "doc/decisions/**", "changes/**"]
# Handover files that every branch shares; edits here are merge-conflict risk.
SHARED_HANDOVER = ["doc/handover/consolidated_handover.md", "doc/handover/*/handover-notes.md",
                   "doc/handover/STATE.md", "doc/handover/archive/README.md"]
BRANCH_RE = re.compile(r"^(feature|fix|chore|hotfix)/")
VALIDATION_RE = re.compile(r"\bunittest\b|\bpytest\b|check_writing|docs\.py|handover\.py\s+check")
DASHES = "—–"

PRE_RECEIVE = """#!/bin/sh
# Scenario origin: main is protected, exactly like branch protection on GitHub.
status=0
while read old new ref; do
  case "$ref" in
    refs/heads/main|refs/heads/master)
      echo "$ref" >> rejected.log
      echo "remote: main is protected; push a branch and open a pull request" >&2
      status=1 ;;
  esac
done
exit $status
"""


# ── scenarios ────────────────────────────────────────────────────────────────

def load_scenarios(directory: Path = SCEN_DIR) -> dict[str, dict]:
    scenarios = {}
    for path in sorted(directory.glob("*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        data["id"] = path.stem
        data.setdefault("allowed_paths", [])
        data.setdefault("expect", {})
        data.setdefault("setup", {})
        scenarios[path.stem] = data
    return scenarios


def select(scenarios: dict, ids: list[str], smoke: bool, everything: bool) -> list[str]:
    if ids:
        unknown = [i for i in ids if i not in scenarios]
        if unknown:
            sys.exit(f"ERROR: unknown scenario(s) {', '.join(unknown)}; see --list")
        chosen = ids
    elif everything:
        chosen = list(scenarios)
    else:
        chosen = [i for i, s in scenarios.items() if s.get("smoke")]
    return [i for i in chosen if not scenarios[i].get("pair_only")]


# ── git helpers ──────────────────────────────────────────────────────────────

def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", message)


def branches(repo: Path) -> list[str]:
    out = git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return [b for b in out.splitlines() if b]


# ── workspace ────────────────────────────────────────────────────────────────

def export_toolkit(ref: str, dest: Path) -> None:
    """Copy the toolkit at `ref` into dest; WORKTREE copies uncommitted files too."""
    dest.mkdir(parents=True)
    if ref == "WORKTREE":
        listing = git(REPO_ROOT, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
        for name in filter(None, listing.split("\0")):
            src = REPO_ROOT / name
            if src.is_file():
                target = dest / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
        return
    archive = subprocess.run(["git", "-C", str(REPO_ROOT), "archive", ref],
                             capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)


def build_base(toolkit_ref: str, base: Path) -> Path:
    """Fixture + toolkit + scaffold, committed on main and pushed to a protected origin."""
    work = base / "work"
    shutil.copytree(FIXTURE, work)
    export_toolkit(toolkit_ref, work / "organisation")
    subprocess.run([sys.executable, str(work / "organisation" / "scripts" / "init_project.py"),
                    "--project-name", PROJECT_NAME, "--departments", "engineering",
                    "--level", "2", "--output-dir", str(work)],
                   capture_output=True, text=True, check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)
    git(work, "config", "user.name", "Scenario Runner")
    git(work, "config", "user.email", "scenario@example.invalid")
    commit_all(work, "chore: project baseline")
    origin = base / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    git(work, "remote", "add", "origin", str(origin))
    git(work, "push", "-q", "origin", "main")
    hook = origin / "hooks" / "pre-receive"
    hook.write_text(PRE_RECEIVE, encoding="utf-8")
    hook.chmod(0o755)
    return work


def clone_base(base: Path, run_dir: Path) -> Path:
    """Copy a built base so every run starts from identical commits."""
    shutil.copytree(base, run_dir, symlinks=True)
    work = run_dir / "work"
    git(work, "remote", "set-url", "origin", str(run_dir / "origin.git"))
    return work


def slug(branch: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", branch.lower()).strip("-")


def seed_handover(work: Path, note: str, branch: str) -> Path:
    """Write a prior agent's handover using whichever layout the toolkit scaffolded."""
    entries = work / "doc" / "handover" / "entries"
    if entries.is_dir():
        path = entries / f"{SEED_DATE}-{slug(branch)}.md"
        path.write_text(
            f"---\nbranch: {branch}\ndept: engineering\nagent: prior-agent\ndate: {SEED_DATE}\n---\n\n"
            f"# {branch}\n\n{note}\n", encoding="utf-8")
        return path
    notes = work / "doc" / "handover" / "engineering" / "handover-notes.md"
    text = notes.read_text(encoding="utf-8")
    marker = "## Work Completed\n"
    at = text.index(marker) + len(marker)
    if text[at:].startswith("<!--"):
        at = text.index("\n", at) + 1
    entry = f"\n### {SEED_DATE} ({branch})\n{note}\n"
    notes.write_text(text[:at] + entry + text[at:], encoding="utf-8")
    return notes


def apply_setup(work: Path, setup: dict) -> list[str]:
    """Create the scenario's starting branch; returns branches that pre-exist the agent."""
    if not setup:
        return []
    branch = setup["branch"]
    git(work, "checkout", "-q", "-b", branch)
    overlay = SCEN_DIR / "overlays" / setup["overlay"]
    for src in overlay.rglob("*"):
        if src.is_file():
            target = work / src.relative_to(overlay)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    if setup.get("handover_note"):
        seed_handover(work, setup["handover_note"].strip(), branch)
    if setup.get("commit"):
        commit_all(work, setup["commit"])
        if not setup.get("stay"):
            git(work, "checkout", "-q", "main")
    return [branch]


def tree_hashes(root: Path) -> dict[str, str]:
    hashes = {}
    for path in root.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            hashes[path.relative_to(root).as_posix()] = hashlib.sha1(path.read_bytes()).hexdigest()
    return hashes


# ── scoring (pure helpers are unit tested) ───────────────────────────────────

def glob_match(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        regex = re.escape(pattern).replace(r"\*\*", "\x00").replace(r"\*", "[^/]*")
        regex = regex.replace("\x00/", "(?:.*/)?").replace("\x00", ".*")
        if re.fullmatch(regex, path):
            return True
    return False


def _norm(line: str) -> str:
    return re.sub(rf"[\s{DASHES},;:.\-]+", "", line)


def dash_churn(patch: str) -> int:
    """Removed lines with an em/en dash that come back identical apart from punctuation."""
    removed = [l[1:] for l in patch.splitlines() if l.startswith("-") and not l.startswith("---")]
    added = {_norm(l[1:]) for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++")}
    return sum(1 for l in removed if any(d in l for d in DASHES) and _norm(l) in added)


MANAGED_RE = re.compile(rb"<!-- BEGIN:(\S+) -->.*?<!-- END:\1 -->", re.S)


def managed_block(content: bytes) -> bytes | None:
    """The first tool-managed block in a file, markers included; None if absent."""
    m = MANAGED_RE.search(content)
    return m.group(0) if m else None


def reads_before_first_edit(events: list[agents.Event]) -> list[str]:
    reads: list[str] = []
    for event in events:
        if event.kind == "edit":
            break
        if event.kind == "read" and event.path and event.path not in reads:
            reads.append(event.path)
    return reads


def worktrees(work: Path) -> list[Path]:
    """The main checkout plus any linked worktrees an agent created (git worktree add)."""
    out = git(work, "worktree", "list", "--porcelain")
    paths = [Path(line[len("worktree "):]) for line in out.splitlines() if line.startswith("worktree ")]
    return [p for p in paths if p.is_dir()] or [work]


def changed_files(work: Path, base: str) -> set[str]:
    files: set[str] = set()
    for branch in branches(work):
        files.update(git(work, "diff", "--name-only", f"{base}..{branch}").splitlines())
    for tree in worktrees(work):
        files.update(git(tree, "diff", "--name-only", "HEAD").splitlines())
        files.update(git(tree, "ls-files", "--others", "--exclude-standard").splitlines())
    return {f for f in files if f}


def all_patches(work: Path, base: str) -> str:
    parts = [git(work, "diff", "-U0", f"{base}..{b}") for b in branches(work)]
    parts += [git(tree, "diff", "-U0", "HEAD") for tree in worktrees(work)]
    return "\n".join(parts)


def dirty(tree: Path) -> bool:
    return git(tree, "status", "--porcelain") != ""


def result_ref(work: Path, base: str, preexisting: list[str]) -> str | None:
    """The commit holding the agent's work: whichever branch or worktree HEAD is
    furthest ahead of the base."""
    candidates = branches(work) + [git(t, "rev-parse", "HEAD") for t in worktrees(work)]
    best, best_count = None, 0
    for ref in candidates:
        count = int(git(work, "rev-list", "--count", f"{base}..{ref}") or 0)
        if count > best_count:
            best, best_count = ref, count
    return best


def test_target(work: Path, base: str, preexisting: list[str]):
    """Where to run the tests: a worktree with uncommitted work, else the furthest ref.
    Returns (path, cleanup) where cleanup removes any temporary checkout."""
    for tree in worktrees(work):
        if dirty(tree):
            return tree, None
    ref = result_ref(work, base, preexisting)
    if not ref or ref == git(work, "rev-parse", "HEAD"):
        return work, None
    tmp = Path(tempfile.mkdtemp(prefix="scen-wt-"))
    git(work, "worktree", "add", "-q", "--detach", str(tmp / "tree"), ref)

    def cleanup():
        git(work, "worktree", "remove", "--force", str(tmp / "tree"), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    return tmp / "tree", cleanup


def run_tests(cwd: Path, start: Path, top: Path) -> bool:
    env = {**os.environ, "PYTHONPATH": str(cwd), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-q",
                             "-s", str(start), "-t", str(top)],
                            cwd=cwd, capture_output=True, text=True, env=env)
    return result.returncode == 0


def score(scen: dict, result: agents.RunResult, run_dir: Path, base: str,
          preexisting: list[str], originals: dict) -> dict:
    work = run_dir / "work"
    expect = scen["expect"]
    files = changed_files(work, base)
    patch = all_patches(work, base)
    allowed = DEFAULT_ALLOWED + scen["allowed_paths"]
    toolkit_after = tree_hashes(work / "organisation")
    toolkit_edits = sorted(k for k in set(originals["toolkit"]) | set(toolkit_after)
                           if originals["toolkit"].get(k) != toolkit_after.get(k))
    new_branches = [b for b in branches(work) if b != "main" and b not in preexisting]
    origin = run_dir / "origin.git"
    rejected = origin / "rejected.log"
    reads = reads_before_first_edit(result.events)
    handover_files = sorted(f for f in files if f.startswith("doc/handover/"))

    block = managed_block(originals["web"])
    web_ok = managed_block((work / "web" / "AGENTS.md").read_bytes()) == block
    for tree in worktrees(work):
        web_ok = web_ok and managed_block((tree / "web" / "AGENTS.md").read_bytes()) == block
    for branch in branches(work):
        shown = subprocess.run(["git", "-C", str(work), "show", f"{branch}:web/AGENTS.md"],
                               capture_output=True)
        web_ok = web_ok and managed_block(shown.stdout) == block

    metrics = {
        "files_changed": sorted(files),
        "out_of_scope_files": sorted(f for f in files if not glob_match(f, allowed)),
        "dash_churn_lines": dash_churn(patch),
        "foreign_block_intact": web_ok,
        "toolkit_files_edited": toolkit_edits,
        "committed_on_main": git(work, "rev-parse", "main") != base,
        "origin_main_moved": git(origin, "rev-parse", "main") != base,
        "main_push_rejections": len(rejected.read_text().splitlines()) if rejected.exists() else 0,
        "new_branches": new_branches,
        "branch_named": (all(BRANCH_RE.match(b) for b in new_branches) and bool(new_branches))
                        if files - set(handover_files) and not preexisting else None,
        "handover_files": handover_files,
        "shared_handover_edits": sorted(f for f in handover_files if glob_match(f, SHARED_HANDOVER)),
        "validation_run": any(e.kind == "shell" and e.cmd and VALIDATION_RE.search(e.cmd)
                              for e in result.events),
        "reads_before_first_edit": reads,
        "context_bytes_before_first_edit": sum(originals["sizes"].get(p, 0) for p in reads),
        "worktree_clean": not any(dirty(t) for t in worktrees(work)),
        "linked_worktrees": [str(t) for t in worktrees(work) if t != work],
        "turns": result.turns, "cost_usd": result.cost_usd, "seconds": result.seconds,
        "usage": result.usage, "timed_out": result.timed_out, "exit_code": result.exit_code,
        "model": result.model,
    }

    checks: dict[str, bool] = {
        "in_scope": not metrics["out_of_scope_files"],
        "no_dash_churn": metrics["dash_churn_lines"] == 0,
        "foreign_block_intact": web_ok,
        "toolkit_untouched": not toolkit_edits,
        "main_untouched": not metrics["committed_on_main"] and not metrics["origin_main_moved"],
        "finished": not result.timed_out,
    }
    if metrics["branch_named"] is not None:
        checks["branch_named"] = metrics["branch_named"]
    if expect.get("no_changes"):
        checks["no_changes"] = not files
    if expect.get("handover"):
        checks["handover_written"] = bool(handover_files)
    if expect.get("validation"):
        checks["validation_run"] = metrics["validation_run"]
    if expect.get("docs_read"):
        seen = {e.path for e in result.events if e.kind == "read"} if expect.get("no_changes") else set(reads)
        checks["docs_found"] = all(d in seen for d in expect["docs_read"])
    if expect.get("answer_contains"):
        reply = result.final_text.lower()
        checks["answer_ok"] = all(k.lower() in reply for k in expect["answer_contains"])
    if expect.get("decision_recorded"):
        added = "\n".join(l for l in patch.splitlines() if l.startswith("+")).lower()
        checks["decision_recorded"] = (any(f.startswith("doc/decisions/") or f == "doc/architecture.md"
                                           for f in files)
                                       or ("decision" in added and bool(handover_files)))
    if expect.get("pushed_branch"):
        name = expect["pushed_branch"]
        remote = subprocess.run(["git", "-C", str(origin), "rev-parse", "--verify", "-q",
                                 f"refs/heads/{name}"], capture_output=True, text=True)
        checks["branch_pushed"] = remote.returncode == 0

    if expect.get("tests"):
        target, cleanup = test_target(work, base, preexisting)
        checks["tests_pass"] = run_tests(target, target / "tests", target)
        hidden = SCEN_DIR / "hidden" / scen["id"]
        if hidden.is_dir():
            staged = run_dir / "hidden"
            shutil.copytree(hidden, staged, dirs_exist_ok=True)
            checks["hidden_tests_pass"] = run_tests(target, staged, staged)
        if cleanup:
            cleanup()

    return {"scenario": scen["id"], "runner": result.runner, "passed": all(checks.values()),
            "checks": checks, "metrics": metrics}


# ── orchestration ────────────────────────────────────────────────────────────

def prepare(base: Path, run_dir: Path, scen: dict):
    work = clone_base(base, run_dir)
    preexisting = apply_setup(work, scen["setup"])
    base_commit = git(work, "rev-parse", "main")
    originals = {
        "web": (work / "web" / "AGENTS.md").read_bytes(),
        "toolkit": tree_hashes(work / "organisation"),
        "sizes": {p.relative_to(work).as_posix(): p.stat().st_size
                  for p in work.rglob("*") if p.is_file() and ".git" not in p.parts},
    }
    return work, preexisting, base_commit, originals


def new_workspace_dir(sid: str) -> Path:
    """Scratch dirs live in the system temp dir, never inside this repo: Claude Code
    loads every CLAUDE.md above its working directory, which would leak the
    toolkit's own instructions into the run."""
    return Path(tempfile.mkdtemp(prefix=f"np-run-{sid}-")) / "run"


def execute(runner: str, scen: dict, base: Path, out_dir: Path, args,
            cleanup: bool = True) -> dict:
    run_dir = new_workspace_dir(scen["id"])
    out_dir.mkdir(parents=True, exist_ok=True)
    work, preexisting, base_commit, originals = prepare(base, run_dir, scen)
    model = args.model_claude if runner == "claude" else args.model_codex
    result = agents.run(runner, work, scen["prompt"].strip(),
                        transcript=out_dir / "transcript.jsonl", timeout=args.timeout,
                        model=model, writable=(run_dir,))
    (out_dir / "reply.md").write_text(result.final_text, encoding="utf-8")
    scored = score(scen, result, run_dir, base_commit, preexisting, originals)
    scored["run_dir"] = str(out_dir)
    scored["workspace"] = str(run_dir)
    if cleanup and not args.keep:
        shutil.rmtree(run_dir.parent, ignore_errors=True)
    return scored


def merge_conflicts(a_run: Path, b_run: Path, base_commit: str) -> dict:
    """Merge both agents' work onto the base, the way two PRs would land."""
    refs = []
    for run_dir in (a_run, b_run):
        work = run_dir / "work"
        for tree in worktrees(work):
            if dirty(tree):
                commit_all(tree, "scenario: snapshot uncommitted work")
        refs.append(result_ref(work, base_commit, []))
    merge = Path(tempfile.mkdtemp(prefix="np-merge-", dir=a_run.parent)) / "repo"
    subprocess.run(["git", "clone", "-q", str(a_run / "work"), str(merge)], check=True)
    git(merge, "config", "user.name", "Scenario Runner")
    git(merge, "config", "user.email", "scenario@example.invalid")
    git(merge, "checkout", "-q", "-b", "integrate", base_commit)
    outcome = {"a_ref": refs[0], "b_ref": refs[1], "conflicted_files": [], "merged": False}
    if not refs[0] or not refs[1]:
        outcome["note"] = "one agent produced no commits"
        return outcome
    commits = []
    for run_dir, ref in ((a_run, refs[0]), (b_run, refs[1])):
        sha = git(run_dir / "work", "rev-parse", ref)
        git(merge, "fetch", "-q", str(run_dir / "work"), sha)
        commits.append(sha)
    for ref in commits:
        done = subprocess.run(["git", "-C", str(merge), "-c", "commit.gpgsign=false", "merge",
                               "--no-edit", "-q", ref], capture_output=True, text=True)
        if done.returncode != 0:
            outcome["conflicted_files"] = git(merge, "diff", "--name-only",
                                              "--diff-filter=U").splitlines()
            return outcome
    outcome["merged"] = True
    return outcome


def execute_pair(runner: str, scen_a: dict, scen_b: dict, base: Path, out_dir: Path, args) -> dict:
    with futures.ThreadPoolExecutor(max_workers=2) as pool:
        fa = pool.submit(execute, runner, scen_a, base, out_dir / "a", args, False)
        fb = pool.submit(execute, runner, scen_b, base, out_dir / "b", args, False)
        a, b = fa.result(), fb.result()
    a_run, b_run = Path(a["workspace"]), Path(b["workspace"])
    merged = merge_conflicts(a_run, b_run, git(base / "work", "rev-parse", "main"))
    if not args.keep:
        for run_dir in (a_run, b_run):
            shutil.rmtree(run_dir.parent, ignore_errors=True)
    a["run_dir"] = str(out_dir)
    a["pair"] = {"with": scen_b["id"], "b": b, **merged}
    a["checks"]["parallel_merge_clean"] = merged["merged"]
    a["metrics"]["parallel_conflicts"] = len(merged["conflicted_files"])
    a["passed"] = all(a["checks"].values()) and b["passed"]
    return a


def summarise(rows: list[dict]) -> dict:
    table: dict = {}
    for row in rows:
        entry = table.setdefault(row["runner"], {}).setdefault(row["scenario"], {
            "runs": 0, "passed": 0, "checks": {}, "dash_churn_lines": 0,
            "out_of_scope_files": 0, "shared_handover_edits": 0, "context_bytes": [],
            "parallel_conflicts": [], "cost_usd": 0.0, "seconds": 0.0})
        entry["runs"] += 1
        entry["passed"] += int(row["passed"])
        for name, ok in row["checks"].items():
            entry["checks"].setdefault(name, 0)
            entry["checks"][name] += int(ok)
        m = row["metrics"]
        entry["dash_churn_lines"] += m["dash_churn_lines"]
        entry["out_of_scope_files"] += len(m["out_of_scope_files"])
        entry["shared_handover_edits"] += len(m["shared_handover_edits"])
        entry["context_bytes"].append(m["context_bytes_before_first_edit"])
        if "parallel_conflicts" in m:
            entry["parallel_conflicts"].append(m["parallel_conflicts"])
        entry["cost_usd"] += m.get("cost_usd") or 0.0
        entry["seconds"] += m.get("seconds") or 0.0
    return table


def render(table: dict) -> str:
    lines = ["| Runner | Scenario | Pass | Failed checks | Churn | Out of scope | Shared handover edits | Context bytes | Conflicts |",
             "|---|---|---|---|---|---|---|---|---|"]
    for runner, scenarios in sorted(table.items()):
        for sid, e in sorted(scenarios.items()):
            failed = ", ".join(f"{k} {e['runs'] - v}/{e['runs']}"
                               for k, v in e["checks"].items() if v < e["runs"]) or "none"
            ctx = round(sum(e["context_bytes"]) / len(e["context_bytes"]))
            conflicts = ",".join(map(str, e["parallel_conflicts"])) or "n/a"
            lines.append(f"| {runner} | {sid} | {e['passed']}/{e['runs']} | {failed} | "
                         f"{e['dash_churn_lines']} | {e['out_of_scope_files']} | "
                         f"{e['shared_handover_edits']} | {ctx} | {conflicts} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run toolkit scenario evals against coding agents")
    parser.add_argument("--list", action="store_true", help="List scenarios and exit")
    parser.add_argument("--scenario", action="append", default=[], help="Scenario id (repeatable)")
    parser.add_argument("--smoke", action="store_true", help="Run the smoke set (default)")
    parser.add_argument("--all", action="store_true", help="Run every scenario")
    parser.add_argument("--runner", default=",".join(agents.RUNNERS),
                        help="Comma-separated runners (default: claude,codex)")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--jobs", type=int, default=3, help="Runs in parallel")
    parser.add_argument("--toolkit-ref", default="WORKTREE",
                        help="Toolkit version under test: WORKTREE (default) or any git ref")
    parser.add_argument("--timeout", type=int, default=1500, help="Seconds per run")
    parser.add_argument("--model-claude")
    parser.add_argument("--model-codex")
    parser.add_argument("--label", help="Name for the results folder")
    parser.add_argument("--keep", action="store_true",
                        help="Keep the scratch workspaces (paths are in each score.json)")
    parser.add_argument("--scorecard", help="Also write the summary JSON to this path")
    parser.add_argument("--setup-only", metavar="SCENARIO",
                        help="Build the workspace for one scenario, print its path, run no agent")
    args = parser.parse_args(argv)

    scenarios = load_scenarios()
    if args.list:
        for sid, scen in scenarios.items():
            tags = [t for t in ("smoke", "pair_only") if scen.get(t)]
            print(f"{sid:22} {scen['title']}{'  [' + ', '.join(tags) + ']' if tags else ''}")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    label = args.label or f"{stamp}-{args.toolkit_ref.replace('/', '-')}"
    out = RESULTS_DIR / label
    base = Path(tempfile.mkdtemp(prefix="np-scenario-base-"))
    shutil.rmtree(base)
    build_base(args.toolkit_ref, base)

    if args.setup_only:
        run_dir = Path(tempfile.mkdtemp(prefix=f"np-scenario-{args.setup_only}-"))
        shutil.rmtree(run_dir)
        prepare(base, run_dir, scenarios[args.setup_only])
        print(run_dir / "work")
        return 0

    runners = [r.strip() for r in args.runner.split(",") if r.strip()]
    missing = [r for r in runners if not agents.available(r)]
    if missing:
        sys.exit(f"ERROR: runner CLI not on PATH: {', '.join(missing)}")
    chosen = select(scenarios, args.scenario, args.smoke, args.all)

    jobs = []
    for runner in runners:
        for sid in chosen:
            for n in range(1, args.repeat + 1):
                jobs.append((runner, sid, n))
    print(f"{len(jobs)} run(s) against toolkit {args.toolkit_ref}; results in {out}", flush=True)

    rows: list[dict] = []
    with futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        pending = {}
        for runner, sid, n in jobs:
            scen = scenarios[sid]
            run_dir = out / runner / f"{sid}-r{n}"  # results only; workspaces are in temp
            if scen.get("pair"):
                fut = pool.submit(execute_pair, runner, scen, scenarios[scen["pair"]], base, run_dir, args)
            else:
                fut = pool.submit(execute, runner, scen, base, run_dir, args)
            pending[fut] = (runner, sid, n)
        for fut in futures.as_completed(pending):
            runner, sid, n = pending[fut]
            try:
                row = fut.result()
            except Exception as exc:  # a broken run must not sink the batch
                print(f"  {runner} {sid} r{n}: ERROR {exc}", flush=True)
                continue
            (Path(row["run_dir"]) / "score.json").write_text(json.dumps(row, indent=2, default=str))
            failed = [k for k, ok in row["checks"].items() if not ok]
            print(f"  {runner} {sid} r{n}: {'PASS' if row['passed'] else 'FAIL'}"
                  f"{'' if not failed else ' (' + ', '.join(failed) + ')'}", flush=True)
            rows.append(row)

    table = summarise(rows)
    summary = {"toolkit_ref": args.toolkit_ref, "date": dt.date.today().isoformat(),
               "runners": runners, "repeat": args.repeat, "scenarios": chosen, "results": table}
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    report = render(table)
    (out / "summary.md").write_text(report + "\n")
    print()
    print(report)
    if args.scorecard:
        Path(args.scorecard).parent.mkdir(parents=True, exist_ok=True)
        Path(args.scorecard).write_text(json.dumps(summary, indent=2) + "\n")
    shutil.rmtree(base, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
