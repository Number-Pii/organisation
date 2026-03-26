#!/usr/bin/env python3
"""
update.py — Number Pii Toolkit Updater

Checks for updates to the organisation toolkit and pulls the latest version safely.
Your project files (doc/) are not in this repo and will never be touched.

Usage:
    python3 scripts/update.py             # Check for updates and prompt to install
    python3 scripts/update.py --check     # Check only, do not update
    python3 scripts/update.py --yes       # Update without prompting
    python3 scripts/update.py --changelog # Show full changelog and exit
"""

import subprocess
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"
CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"


def read_version(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def run(cmd: list[str], capture=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=capture, text=True)


def is_git_repo() -> bool:
    result = run(["git", "rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0


def fetch_remote() -> bool:
    result = run(["git", "fetch", "--quiet"])
    return result.returncode == 0


def get_current_commit() -> str:
    return run(["git", "rev-parse", "HEAD"]).stdout.strip()


def get_remote_commit() -> str:
    result = run(["git", "rev-parse", "@{u}"])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_remote_version() -> str:
    """Read VERSION from the remote without checking it out."""
    result = run(["git", "show", "origin/main:VERSION"])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_commits_behind() -> list[str]:
    """Return one-line summaries of commits on remote that aren't local."""
    result = run(["git", "log", "HEAD..@{u}", "--oneline"])
    if result.returncode != 0:
        return []
    lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
    return lines


def pull() -> bool:
    result = run(["git", "pull", "--ff-only"], capture=False)
    return result.returncode == 0


def show_changelog(since_version: str = None):
    if not CHANGELOG_FILE.exists():
        print("No CHANGELOG.md found.")
        return
    content = CHANGELOG_FILE.read_text(encoding="utf-8")
    if since_version:
        # Print only sections at or after the given version
        lines = content.splitlines()
        printing = False
        for line in lines:
            if line.startswith(f"## [{since_version}]"):
                printing = True
            if printing:
                print(line)
    else:
        print(content)


def main():
    parser = argparse.ArgumentParser(description="Update the Number Pii Organisation Toolkit")
    parser.add_argument("--check",     action="store_true", help="Check for updates only, do not pull")
    parser.add_argument("--yes",       action="store_true", help="Update without prompting")
    parser.add_argument("--changelog", action="store_true", help="Show full changelog and exit")
    args = parser.parse_args()

    if args.changelog:
        show_changelog()
        return

    current_version = read_version(VERSION_FILE) if VERSION_FILE.exists() else "unknown"
    print(f"Number Pii Organisation Toolkit — Update Check")
    print(f"Current version: {current_version}")
    print()

    if not is_git_repo():
        print("This directory is not a git repository.")
        print("To enable updates, clone the repo:")
        print("  git clone https://github.com/olatunbosun-iyare/organisation.git")
        sys.exit(1)

    print("Fetching remote...", end=" ", flush=True)
    if not fetch_remote():
        print("failed.")
        print("Could not reach remote. Check your internet connection.")
        sys.exit(1)
    print("done.")

    remote_version = get_remote_version()
    commits_behind = get_commits_behind()

    if not commits_behind:
        print("You are already up to date.")
        return

    print(f"Latest version:  {remote_version or 'unknown'}")
    print(f"Updates available: {len(commits_behind)} commit(s)")
    print()

    # Determine if this is a major bump
    is_major = False
    if current_version != "unknown" and remote_version:
        current_major = current_version.split(".")[0]
        remote_major = remote_version.split(".")[0]
        is_major = remote_major > current_major

    if is_major:
        print("⚠  MAJOR version update detected.")
        print("   The Initialize Protocol may have changed.")
        print("   Your existing doc/ files are safe, but read the migration notes")
        print("   in CHANGELOG.md before re-initializing any project sessions.")
        print()

    print("What's new:")
    for commit in commits_behind:
        print(f"  • {commit}")
    print()

    if CHANGELOG_FILE.exists() and remote_version:
        print(f"Run `python3 scripts/update.py --changelog` to see full release notes.")
        print()

    if args.check:
        print("(Run without --check to install the update.)")
        return

    if not args.yes:
        answer = input("Update now? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Update cancelled.")
            return

    print()
    print("Updating...")
    if pull():
        new_version = read_version(VERSION_FILE) if VERSION_FILE.exists() else "unknown"
        print(f"Updated to version {new_version}.")
        print()
        print("Your project doc/ files are untouched.")
        if is_major:
            print("Read the migration notes in CHANGELOG.md before starting new sessions.")
    else:
        print("Update failed. You may have local changes that conflict.")
        print("Run `git status` to inspect, then try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
