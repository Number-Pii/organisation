#!/usr/bin/env python3
"""
migrate_consumer.py: Move a Pre-4.0 Project to the v4 Layout

Opt-in and dry-run by default: it prints what it would change and writes
nothing until you pass --apply. It never commits; review `git diff` on a
branch and open a PR as usual.

What it does:
- doc/handover/consolidated_handover.md becomes doc/handover/STATE.md (content
  kept, front matter added). The old department notes stay where they are,
  frozen, and STATE.md links to them.
- Adds doc/handover/entries/README.md and a doc/README.md map that lists the
  documents already in doc/.
- Replaces toolkit-generated context pointers (files that start with
  "# <name>: AI Assistant Context Contract" and a "_Generated ... by Number Pii
  toolkit_" line): AGENTS.md gets the v4 layout with the managed block, and
  CLAUDE.md and GEMINI.md become stubs. Text someone appended after the
  standard ending is carried into AGENTS.md. Hand-written files are never
  touched.
- Adds the git pre-push hook, removes the SessionStart checklist hook, and
  updates an unmodified Claude protect-main hook to the worktree-aware version.
- Replaces the scaffold's never-resolving placeholder link in team-assignment.md.
- Leaves doc/workflow.md Status columns alone unless --strip-status is passed.

Usage (from the consuming project root):
    python3 organisation/scripts/migrate_consumer.py            # dry run
    python3 organisation/scripts/migrate_consumer.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs  # noqa: E402
from init_project import LEVELS, level_context, load_raw, render  # noqa: E402

POINTER_TITLE = re.compile(r"^# (.+): AI Assistant Context Contract\s*$")
POINTER_SIGNATURE = re.compile(r"^_Generated.*Number Pii toolkit.*_\s*$")
LEVEL_LINE = re.compile(r"Project classification: Level (\d)")
POINTER_END = "There are no exceptions for urgency, convenience, or confidence."
V3_HOOK_MARKER = "Blocked by the toolkit"
STATUS_HEADER = "| # | Task | Owner | Type | Depends On | Status |"
# A toolkit-written placeholder link that never resolved in any project.
V3_ROLE_LINK = "- [Role Name](../Teams/[department]/[role-file].md)"
V4_ROLE_LINE = "- Role name: `organisation/Teams/<department>/<role-file>.md`"


class Plan:
    def __init__(self, root: Path):
        self.root = root
        self.writes: dict[Path, str] = {}
        self.moves: list[tuple[Path, Path]] = []
        self.deletes: list[Path] = []
        self.notes: list[str] = []

    def write(self, path: Path, content: str, why: str):
        self.writes[path] = content
        self.notes.append(f"write   {path.relative_to(self.root)}: {why}")

    def keep(self, path: Path, why: str):
        self.notes.append(f"keep    {path.relative_to(self.root)}: {why}")


def generated_pointer(text: str) -> tuple[str, int | None, str] | None:
    """(project name, level, carried-over tail) for a toolkit-generated pointer, else None."""
    lines = text.splitlines()
    if len(lines) < 3 or not POINTER_TITLE.match(lines[0]):
        return None
    if not any(POINTER_SIGNATURE.match(l) for l in lines[1:4]):
        return None
    name = POINTER_TITLE.match(lines[0]).group(1)
    m = LEVEL_LINE.search(text)
    tail = text.split(POINTER_END, 1)[1].strip() if POINTER_END in text else ""
    return name, int(m.group(1)) if m else None, tail


def plan_context_files(plan: Plan, level_override: int | None):
    root = plan.root
    agents = root / "AGENTS.md"
    info = None
    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        path = root / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "<!-- np:begin -->" in text or "@AGENTS.md" in text:
            plan.keep(path, "already on the v4 layout")
            continue
        parsed = generated_pointer(text)
        if not parsed:
            plan.keep(path, "hand-written; never rewritten. To add the toolkit block, run "
                            "sync_context.py --append on it" if name == "AGENTS.md" else
                            "hand-written; never rewritten")
            continue
        info = info or parsed
        if name == "AGENTS.md":
            continue
        stub = load_raw("claude-stub.md" if name == "CLAUDE.md" else "gemini-stub.md")
        plan.write(path, stub, "generated pointer becomes an @AGENTS.md stub")

    agents_text = agents.read_text(encoding="utf-8") if agents.exists() else None
    agents_parsed = generated_pointer(agents_text) if agents_text else None
    if agents_text is None or agents_parsed:
        source = agents_parsed or info
        if not source:
            plan.notes.append("skip    AGENTS.md: no generated pointer to take the project name "
                              "from; create it with init_project.py")
            return
        name, level, tail = source
        level = level_override or level
        if level not in LEVELS:
            plan.notes.append("skip    AGENTS.md: level unknown; re-run with --level N")
            return
        body = render("agents-root.md", project_name=name, today="",
                      agents_block=load_raw("agents-block.md"), **level_context(level))
        if tail:
            body = body.replace("\n<!-- np:begin -->",
                                f"\n## Carried over from the previous context file\n\n{tail}\n\n"
                                "<!-- np:begin -->", 1)
        why = "v4 layout with the toolkit's managed block"
        if tail:
            why += f" ({len(tail.splitlines())} appended lines carried over)"
        plan.write(agents, body, why)


def plan_handover(plan: Plan):
    root = plan.root
    handover = root / "doc" / "handover"
    state = handover / "STATE.md"
    legacy = handover / "consolidated_handover.md"
    if state.exists():
        plan.keep(state, "already present")
    elif legacy.exists():
        notes = sorted(handover.glob("*/handover-notes.md"))
        frozen = "\n".join(f"- `{p.relative_to(root / 'doc').as_posix()}`" for p in notes)
        preface = ("---\nconsolidated_through: none\n---\n"
                   "<!-- Migrated from consolidated_handover.md. From now on this file changes\n"
                   "     only in chore/handover-consolidate-* PRs; branches write their own\n"
                   "     entries in entries/. -->\n\n")
        if frozen:
            preface += ("Earlier department handover notes are frozen and kept for reference:\n"
                        f"{frozen}\n\n")
        plan.write(state, preface + legacy.read_text(encoding="utf-8"),
                   "consolidated_handover.md content with v4 front matter")
        plan.deletes.append(legacy)
        plan.notes.append(f"remove  {legacy.relative_to(root)}: its content now lives in STATE.md")
    entries_readme = handover / "entries" / "README.md"
    if not entries_readme.exists():
        plan.write(entries_readme, load_raw("handover-entries-README.md"), "per-branch entries folder")


def plan_doc_map(plan: Plan, project_name: str):
    root = plan.root
    doc = root / "doc"
    readme = doc / "README.md"
    if readme.exists() or not doc.is_dir():
        if readme.exists():
            plan.keep(readme, "doc map already present")
        return
    base = render("doc-README.md", project_name=project_name)
    known = {m.split("/")[0] for m in re.findall(r"`([\w./-]+)`", base)}
    extra = []
    for child in sorted(doc.iterdir()):
        if child.name.startswith(".") or child.name == "README.md":
            continue
        label = child.name + ("/" if child.is_dir() else "")
        if child.name in known:
            continue
        if child.is_file() and child.suffix != ".md":
            continue
        summary = docs.summary(child) if child.is_file() else "Folder carried over from before the doc map"
        summary = (summary or "[FILL IN]").replace("|", "/")
        extra.append(f"| `{label}` | {summary} | [FILL IN] |")
    if extra:
        marker = "\n\nFiles inside these folders"
        base = base.replace(marker, "\n" + "\n".join(extra) + marker, 1)
    plan.write(readme, base, f"doc map ({len(extra)} existing documents listed)")


def plan_hooks(plan: Plan):
    root = plan.root
    pre_push = root / ".githooks" / "pre-push"
    if not pre_push.exists():
        plan.write(pre_push, load_raw("pre-push"), "git-native guard against pushes to main")
    checklist = root / ".claude" / "hooks" / "context-checklist.md"
    if checklist.exists():
        plan.deletes.append(checklist)
        plan.notes.append(f"remove  {checklist.relative_to(root)}: SessionStart checklist retired")
    settings = root / ".claude" / "settings.json"
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except ValueError:
            plan.keep(settings, "not valid JSON; edit by hand")
            data = None
        if data:
            session = data.get("hooks", {}).get("SessionStart", [])
            kept = [e for e in session if "context-checklist" not in json.dumps(e)]
            if kept != session:
                if kept:
                    data["hooks"]["SessionStart"] = kept
                else:
                    data["hooks"].pop("SessionStart")
                plan.write(settings, json.dumps(data, indent=2) + "\n",
                           "drop the SessionStart checklist hook")
    hook = root / ".claude" / "hooks" / "protect_main.py"
    if hook.exists() and V3_HOOK_MARKER in hook.read_text(encoding="utf-8"):
        plan.write(hook, load_raw("claude-protect-main.py"), "worktree-aware protect-main hook")


def plan_workflow(plan: Plan, strip: bool):
    wf = plan.root / "doc" / "workflow.md"
    if not wf.exists() or STATUS_HEADER not in wf.read_text(encoding="utf-8"):
        return
    if not strip:
        plan.notes.append("note    doc/workflow.md has Status columns; live status now belongs on "
                          "the board (pass --strip-status to remove them)")
        return
    out = []
    for line in wf.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and line.count("|") >= 7:
            cells = line.split("|")
            line = "|".join(cells[:-2] + [""])
        out.append(line)
    plan.write(wf, "\n".join(out) + "\n", "Status columns removed")


def plan_team_link(plan: Plan):
    team = plan.root / "doc" / "team-assignment.md"
    if team.exists() and V3_ROLE_LINK in team.read_text(encoding="utf-8"):
        plan.write(team, team.read_text(encoding="utf-8").replace(V3_ROLE_LINK, V4_ROLE_LINE),
                   "replace the scaffold's placeholder link, which never resolved")


def build_plan(root: Path, level: int | None, strip_status: bool) -> Plan:
    plan = Plan(root)
    plan_context_files(plan, level)
    name = root.name
    for p in plan.writes:
        if p.name == "AGENTS.md":
            name = plan.writes[p].splitlines()[0].lstrip("# ").strip()
    plan_handover(plan)
    plan_doc_map(plan, name)
    plan_hooks(plan)
    plan_workflow(plan, strip_status)
    plan_team_link(plan)
    return plan


def apply(plan: Plan) -> None:
    for path, content in plan.writes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if path.name == "pre-push":
            path.chmod(0o755)
    for path in plan.deletes:
        path.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Move a pre-4.0 project to the v4 layout")
    parser.add_argument("--project", default=".", help="Consuming project root (default: .)")
    parser.add_argument("--apply", action="store_true", help="Make the changes (default: dry run)")
    parser.add_argument("--level", type=int, choices=sorted(LEVELS),
                        help="Classification level, if the old pointer does not state it")
    parser.add_argument("--strip-status", action="store_true",
                        help="Remove Status columns from doc/workflow.md")
    args = parser.parse_args(argv)

    root = Path(args.project).resolve()
    if (root / "scripts" / "migrate_consumer.py").exists() and (root / "templates").is_dir():
        print("ERROR: this is the toolkit itself; run from a consuming project root.")
        return 1
    plan = build_plan(root, args.level, args.strip_status)
    print(("Applying" if args.apply else "Dry run: nothing written.") + f" Project: {root}\n")
    for note in plan.notes:
        print(f"  {note}")
    if not plan.writes and not plan.deletes:
        print("\nNothing to migrate.")
        return 0
    if args.apply:
        apply(plan)
        print("\nDone. Review `git diff`, enable the push guard with "
              "`git config core.hooksPath .githooks`, and commit on a chore/ branch.")
    else:
        print("\nRe-run with --apply to make these changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
