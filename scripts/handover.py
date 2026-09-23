#!/usr/bin/env python3
"""
handover.py: Number Pii Branch Handover

Handover in a consuming project is one file per branch under
doc/handover/entries/, edited only by that branch, plus doc/handover/STATE.md,
which changes only in consolidation PRs. Parallel branches therefore never
touch the same handover lines.

Subcommands (run from the consuming project root):
    new          Create this branch's entry, pre-filled from its commits
    status       What is in flight: entries on every local and remote branch
    check        Fail a PR that edits another branch's entry or STATE.md
    consolidate  Draft the STATE.md update from entries not yet consolidated

Usage:
    python3 organisation/scripts/handover.py new --issue 12
    python3 organisation/scripts/handover.py status
    python3 organisation/scripts/handover.py check --base origin/main
    python3 organisation/scripts/handover.py consolidate [--mark]
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path
from string import Template

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.frontmatter import parse_frontmatter  # noqa: E402

TOOLKIT = Path(__file__).resolve().parent.parent
TEMPLATE = TOOLKIT / "templates" / "handover-entry.md"
ENTRIES = Path("doc/handover/entries")
STATE = Path("doc/handover/STATE.md")
LEGACY_STATE = Path("doc/handover/consolidated_handover.md")
CONSOLIDATION_BRANCH = re.compile(r"^chore/handover-consolidate-")
ENTRY_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
COMMIT_ORDER = ["feat", "fix", "refactor", "perf", "test", "docs", "chore", "other"]


def git(project: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.exit(f"ERROR: git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def slug(branch: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", branch.lower()).strip("-")


def current_branch(project: Path) -> str:
    return git(project, "branch", "--show-current", check=False)


def default_base(project: Path) -> str:
    for ref in ("origin/main", "main", "origin/master", "master"):
        if git(project, "rev-parse", "--verify", "-q", ref, check=False):
            return ref
    return "HEAD"


def own_entry(project: Path, branch: str) -> Path | None:
    folder = project / ENTRIES
    if not folder.is_dir():
        return None
    for path in sorted(folder.glob("*.md")):
        m = ENTRY_NAME.match(path.name)
        if m and m.group(2) == slug(branch):
            return path
    return None


def commit_lines(project: Path, base: str) -> list[str]:
    """This branch's commits since it left the base, grouped by commit type."""
    out = git(project, "log", f"{base}..HEAD", "--no-merges", "--pretty=format:%h\t%s", check=False)
    groups: dict[str, list[str]] = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        sha, subject = line.split("\t", 1)
        m = re.match(r"^(\w+)(?:\([^)]*\))?!?:\s*(.+)$", subject)
        kind, text = (m.group(1).lower(), m.group(2)) if m else ("other", subject)
        groups.setdefault(kind, []).append(f"- {kind}: {text} ({sha})")
    lines = []
    for kind in COMMIT_ORDER + sorted(k for k in groups if k not in COMMIT_ORDER):
        lines.extend(groups.get(kind, []))
    return lines


# ── new ──────────────────────────────────────────────────────────────────────

def cmd_new(args) -> int:
    project = Path(args.project).resolve()
    branch = args.branch or current_branch(project)
    if not branch or branch in ("main", "master"):
        print("ERROR: create a feature/, fix/, chore/ or hotfix/ branch first; "
              "handover entries belong to a branch.")
        return 1
    existing = own_entry(project, branch)
    if existing:
        print(f"{existing.relative_to(project)} already exists; update it rather than starting another.")
        return 0
    today = args.date or datetime.date.today().isoformat()
    text = Template(TEMPLATE.read_text(encoding="utf-8")).substitute(
        branch=branch, dept=args.dept, agent=args.agent, today=today)
    if args.issue:
        text = text.replace("\nissue:\n", f"\nissue: {args.issue}\n", 1)
    commits = commit_lines(project, args.base or default_base(project))
    if commits:
        text = text.replace("- [What is finished and committed.]", "\n".join(commits), 1)
    path = project / ENTRIES / f"{today}-{slug(branch)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Created {path.relative_to(project)}; fill in the goal, next steps, and decisions.")
    return 0


# ── status ───────────────────────────────────────────────────────────────────

def consolidated_through(text: str) -> str:
    """The last consolidated entry date, or '' before the first consolidation."""
    m = re.search(r"^consolidated_through:\s*(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    return m.group(1) if m else ""


def entries_on(project: Path, ref: str) -> list[str]:
    out = git(project, "ls-tree", "--name-only", f"{ref}:{ENTRIES.as_posix()}", check=False)
    return [n for n in out.splitlines() if ENTRY_NAME.match(n)]


def cmd_status(args) -> int:
    project = Path(args.project).resolve()
    state = project / STATE
    if not state.exists():
        if (project / LEGACY_STATE).exists():
            print("This project still uses the pre-4.0 handover layout "
                  "(doc/handover/consolidated_handover.md).")
            print("Run `python3 organisation/scripts/migrate_consumer.py --dry-run` to see the move.")
            return 0
        print(f"No {STATE} yet; scaffold with init_project.py first.")
        return 1
    through = consolidated_through(state.read_text(encoding="utf-8"))
    base = default_base(project)
    merged = set(entries_on(project, base))
    refs = git(project, "for-each-ref", "--format=%(refname:short)",
               "refs/heads", "refs/remotes", check=False).splitlines()
    rows: dict[str, set[str]] = {}
    for ref in refs:
        if ref.endswith("/HEAD") or ref in (base, "main", "master", "origin/main", "origin/master"):
            continue
        for name in entries_on(project, ref):
            if name not in merged:
                rows.setdefault(name, set()).add(ref)
    pending = sorted(n for n in merged if ENTRY_NAME.match(n).group(1) > through)

    print(f"STATE.md consolidated through {through or 'never'}.")
    print(f"\nIn flight ({len(rows)} branch entr{'y' if len(rows) == 1 else 'ies'} not yet on {base}):")
    for name in sorted(rows):
        print(f"  {name}  [{', '.join(sorted(rows[name]))}]")
    print(f"\nMerged but not consolidated ({len(pending)}):")
    for name in pending:
        print(f"  {name}")
    if len(pending) >= args.threshold:
        print(f"\n{len(pending)} entries are waiting: open a chore/handover-consolidate-"
              f"{datetime.date.today().isoformat()} branch and run `handover.py consolidate`.")
    return 0


# ── check ────────────────────────────────────────────────────────────────────

def classify(files: list[str], branch: str) -> tuple[list[str], list[str]]:
    """(failures, warnings) for a branch's changed files."""
    fails, warns = [], []
    consolidating = bool(CONSOLIDATION_BRANCH.match(branch))
    entries = [f for f in files if f.startswith(ENTRIES.as_posix() + "/") and ENTRY_NAME.match(Path(f).name)]
    own = [f for f in entries if ENTRY_NAME.match(Path(f).name).group(2) == slug(branch)]
    if not consolidating:
        for f in sorted(set(entries) - set(own)):
            fails.append(f"{f} belongs to another branch; each branch edits only its own entry")
        if STATE.as_posix() in files:
            fails.append(f"{STATE} changes only on a chore/handover-consolidate-* branch")
        code = [f for f in files if not f.startswith("doc/") and not f.startswith("changes/")]
        if code and not own:
            warns.append(f"no handover entry for {branch}; run `handover.py new` "
                         f"(expected {ENTRIES}/<date>-{slug(branch)}.md)")
    return fails, warns


def cmd_check(args) -> int:
    project = Path(args.project).resolve()
    branch = args.branch or current_branch(project)
    base = args.base or default_base(project)
    files = git(project, "diff", "--name-only", f"{base}...HEAD").splitlines()
    fails, warns = classify(files, branch)
    for w in warns:
        print(f"WARN  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    if not fails:
        print(f"OK: handover changes on {branch} are confined to its own entry.")
    return 1 if fails else 0


# ── consolidate ──────────────────────────────────────────────────────────────

def section(text: str, heading: str) -> str:
    m = re.search(rf"^## {heading}\s*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    body = m.group(1).strip() if m else ""
    return "" if body.startswith("[") or body.startswith("- [") or body.startswith("1. [") else body


def cmd_consolidate(args) -> int:
    project = Path(args.project).resolve()
    state = project / STATE
    if not state.exists():
        print(f"No {STATE}; nothing to consolidate into.")
        return 1
    through = consolidated_through(state.read_text(encoding="utf-8"))
    folder = project / ENTRIES
    fresh = [p for p in sorted(folder.glob("*.md")) if ENTRY_NAME.match(p.name)
             and ENTRY_NAME.match(p.name).group(1) > through] if folder.is_dir() else []
    if not fresh:
        print(f"Nothing to consolidate: no entries after {through or 'the start'}.")
        return 0

    print(f"# Draft for {STATE} (entries after {through or 'the start'})\n")
    print("Fold these into STATE.md's sections by judgement. Promote durable")
    print("decisions to their own files in doc/decisions/.\n")
    for path in fresh:
        text = path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(path)
        print(f"## {path.name} ({fm.get('branch', '?')})")
        for heading in ("Goal", "Done", "Next", "Decisions", "Gotchas"):
            body = section(text, heading)
            if body:
                print(f"**{heading}:**\n{body}\n")
    latest = max(ENTRY_NAME.match(p.name).group(1) for p in fresh)
    branch = current_branch(project)
    if args.mark:
        if not CONSOLIDATION_BRANCH.match(branch):
            print("ERROR: --mark belongs on a chore/handover-consolidate-* branch.")
            return 1
        text = state.read_text(encoding="utf-8")
        if re.search(r"^consolidated_through:", text, re.MULTILINE):
            text = re.sub(r"^consolidated_through:.*$", f"consolidated_through: {latest}", text,
                          count=1, flags=re.MULTILINE)
        else:
            text = f"---\nconsolidated_through: {latest}\n---\n" + text
        state.write_text(text, encoding="utf-8")
        print(f"Marked {STATE} consolidated through {latest}.")
    else:
        print(f"(After editing STATE.md, run with --mark to record consolidation through {latest}.)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Per-branch handover for Number Pii projects")
    parser.add_argument("--project", default=".", help="Consuming project root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="Create this branch's handover entry")
    new.add_argument("--branch")
    new.add_argument("--issue")
    new.add_argument("--dept", default="engineering")
    new.add_argument("--agent", default="")
    new.add_argument("--base", help="Base ref for the commit list (default: origin/main or main)")
    new.add_argument("--date", help=argparse.SUPPRESS)
    new.set_defaults(func=cmd_new)

    status = sub.add_parser("status", help="Show in-flight and unconsolidated entries")
    status.add_argument("--threshold", type=int, default=5,
                        help="Suggest consolidating at this many merged entries (default 5)")
    status.set_defaults(func=cmd_status)

    check = sub.add_parser("check", help="Check a branch's handover edits (for CI or pre-push)")
    check.add_argument("--base")
    check.add_argument("--branch")
    check.set_defaults(func=cmd_check)

    consolidate = sub.add_parser("consolidate", help="Draft the STATE.md update")
    consolidate.add_argument("--mark", action="store_true",
                             help="Record the consolidation date in STATE.md")
    consolidate.set_defaults(func=cmd_consolidate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
