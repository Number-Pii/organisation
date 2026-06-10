#!/usr/bin/env python3
"""
check_handover.py: Number Pii Handover Staleness Checker

Flags a consolidated handover that has fallen behind the work it describes.
The check compares the last commit that touched the handover file against the
number of commits made to the repository since then. A project that has moved
N commits without a handover update is drifting away from its documented state.

Run from a consuming project root (where doc/ lives):
    python3 organisation/scripts/check_handover.py
    python3 organisation/scripts/check_handover.py --max-commits 10
    python3 organisation/scripts/check_handover.py --path doc/handover/consolidated_handover.md

Exit codes:
    0: handover is fresh (or repository has no commits yet)
    1: handover is stale, missing, or the check could not run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_PATH = "doc/handover/consolidated_handover.md"
DEFAULT_MAX_COMMITS = 20


def git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check consolidated handover freshness")
    parser.add_argument("--path", default=DEFAULT_PATH,
                        help=f"Handover file to check (default: {DEFAULT_PATH})")
    parser.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS,
                        help=f"Commits allowed since the last handover update (default: {DEFAULT_MAX_COMMITS})")
    args = parser.parse_args()

    handover = Path(args.path)
    if not handover.exists():
        print(f"STALE: {handover} does not exist. Scaffold it with init_project.py "
              "or restore it; the project has no documented current state.")
        return 1

    if git("rev-parse", "--git-dir") is None:
        print("ERROR: not a git repository (or git is unavailable); cannot measure staleness.")
        return 1

    last_touch = git("log", "-1", "--format=%H", "--", str(handover))
    if not last_touch:
        print(f"WARN: {handover} has never been committed. Commit it so freshness can be tracked.")
        return 1

    since = git("rev-list", "--count", f"{last_touch}..HEAD")
    if since is None:
        print("ERROR: could not count commits since the last handover update.")
        return 1

    commits_since = int(since)
    when = git("log", "-1", "--format=%cs", "--", str(handover))

    if commits_since > args.max_commits:
        print(f"STALE: {handover} last updated {when} ({commits_since} commits ago, "
              f"limit {args.max_commits}).")
        print("Update the handover before further work; the documented state no "
              "longer matches the repository.")
        return 1

    print(f"OK: {handover} updated {when}, {commits_since} commit(s) ago "
          f"(limit {args.max_commits}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
