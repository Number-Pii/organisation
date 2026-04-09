#!/usr/bin/env python3
"""
check_version.py — Number Pii Version Sync Validator

Checks that the version number is consistent across:
  - VERSION
  - CHANGELOG.md (latest heading)
  - CLAUDE.md (protocol version line)
  - GEMINI.md (protocol version line)

Exit code 0 = all in sync, 1 = mismatch found.

Usage:
    python3 scripts/check_version.py
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def get_version_file():
    """Read version from VERSION file."""
    path = REPO_ROOT / "VERSION"
    return path.read_text(encoding="utf-8").strip()


def get_changelog_version():
    """Extract latest version heading from CHANGELOG.md (e.g. '## [3.4.0] — ...')."""
    path = REPO_ROOT / "CHANGELOG.md"
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## \[(\d+\.\d+\.\d+)\]", line)
        if m:
            return m.group(1)
    return None


def get_md_protocol_version(filename):
    """Extract toolkit version from CLAUDE.md or GEMINI.md (_Version: X.Y — ...)."""
    path = REPO_ROOT / filename
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"_Version:\s*([\d.]+)", line)
        if m:
            return m.group(1)
    return None


def main():
    version_file = get_version_file()
    changelog    = get_changelog_version()
    claude_ver   = get_md_protocol_version("CLAUDE.md")
    gemini_ver   = get_md_protocol_version("GEMINI.md")

    sources = {
        "VERSION":      version_file,
        "CHANGELOG.md": changelog,
    }

    # Protocol version (in CLAUDE.md/GEMINI.md) is a separate number from the toolkit version.
    # But CLAUDE.md and GEMINI.md must match each other.
    protocol_sources = {
        "CLAUDE.md": claude_ver,
        "GEMINI.md": gemini_ver,
    }

    errors = []

    # Check toolkit version sync: VERSION vs CHANGELOG
    if changelog and changelog != version_file:
        errors.append(
            f"  VERSION says {version_file}, CHANGELOG.md says {changelog}"
        )

    # Check protocol version sync: CLAUDE.md vs GEMINI.md
    if claude_ver != gemini_ver:
        errors.append(
            f"  CLAUDE.md protocol version {claude_ver} != GEMINI.md protocol version {gemini_ver}"
        )

    if errors:
        print("VERSION SYNC FAILED:")
        for e in errors:
            print(e)
        print()
        print(f"  VERSION file:             {version_file}")
        print(f"  CHANGELOG.md latest:      {changelog}")
        print(f"  CLAUDE.md protocol:       {claude_ver}")
        print(f"  GEMINI.md protocol:       {gemini_ver}")
        sys.exit(1)
    else:
        print(f"All versions in sync.")
        print(f"  Toolkit version:          {version_file}")
        print(f"  Protocol version:         {claude_ver}")
        sys.exit(0)


if __name__ == "__main__":
    main()
