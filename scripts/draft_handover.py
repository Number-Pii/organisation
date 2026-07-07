#!/usr/bin/env python3
"""
draft_handover.py: Number Pii Handover Drafter

Drafts a dated Work Completed entry for a department handover file from the
consuming project's git history, so the handover discipline costs one review
instead of one archaeology session. The draft is a starting point: review it,
add the why, then commit.

Usage (from the consuming project root):
    python3 organisation/scripts/draft_handover.py                    # print a draft
    python3 organisation/scripts/draft_handover.py --since "7 days"   # explicit window
    python3 organisation/scripts/draft_handover.py --dept engineering --write
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path


def git_log(project: Path, since: str) -> list[tuple[str, str]]:
    """(short_hash, subject) pairs for commits in the window, newest first."""
    result = subprocess.run(
        ["git", "-C", str(project), "log", f"--since={since}",
         "--no-merges", "--pretty=format:%h\t%s"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"ERROR: git log failed in {project}: {result.stderr.strip()}")
    pairs = []
    for line in result.stdout.splitlines():
        if "\t" in line:
            h, s = line.split("\t", 1)
            pairs.append((h.strip(), s.strip()))
    return pairs


def last_entry_date(handover: Path) -> str | None:
    """The most recent '### YYYY-MM-DD' heading in a handover file."""
    if not handover.exists():
        return None
    dates = re.findall(r"^### (\d{4}-\d{2}-\d{2})", handover.read_text(encoding="utf-8"),
                       re.MULTILINE)
    return max(dates) if dates else None


def draft_entry(commits: list[tuple[str, str]], today: str) -> str:
    """A dated Work Completed entry grouped by conventional-commit type."""
    groups: dict[str, list[str]] = {}
    for h, subject in commits:
        m = re.match(r"^(\w+)(?:\([^)]*\))?!?:\s*(.+)$", subject)
        kind, text = (m.group(1).lower(), m.group(2)) if m else ("other", subject)
        groups.setdefault(kind, []).append(f"{text} ({h})")

    order = ["feat", "fix", "refactor", "perf", "test", "docs", "chore", "other"]
    lines = [f"### {today}", "<!-- Drafted from git history by draft_handover.py; "
             "review, add the why, then keep. -->"]
    for kind in order + sorted(k for k in groups if k not in order):
        if kind not in groups:
            continue
        for item in groups[kind]:
            lines.append(f"- {kind}: {item}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Draft a handover entry from git history")
    parser.add_argument("--project", default=".", help="Consuming project root (default: .)")
    parser.add_argument("--dept", default="engineering",
                        help="Department handover folder (default: engineering)")
    parser.add_argument("--since", help='Git time window (default: since the last dated '
                                        'entry in the handover file, else "14 days")')
    parser.add_argument("--write", action="store_true",
                        help="Append the draft to the department handover file")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    handover = project / "doc" / "handover" / args.dept / "handover-notes.md"

    since = args.since or last_entry_date(handover) or "14 days"
    commits = git_log(project, since)
    if not commits:
        print(f"No commits since {since}; nothing to draft.")
        return 0

    today = datetime.date.today().isoformat()
    entry = draft_entry(commits, today)

    if not args.write:
        print(entry)
        print(f"({len(commits)} commit(s) since {since}; re-run with --write to append "
              f"to {handover})", file=sys.stderr)
        return 0

    if not handover.exists():
        sys.exit(f"ERROR: {handover} not found; scaffold the project first or pass --dept.")
    text = handover.read_text(encoding="utf-8")
    marker = "## Work Completed"
    if marker not in text:
        sys.exit(f"ERROR: no '{marker}' section in {handover}.")
    head, tail = text.split(marker, 1)
    # Insert the new dated entry directly under the section heading, most recent first.
    new_text = f"{head}{marker}\n\n{entry}{tail.lstrip()}"
    handover.write_text(new_text, encoding="utf-8")
    print(f"Appended a {today} entry ({len(commits)} commits) to {handover}")
    print("Review the draft: add decisions and context git history cannot carry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
