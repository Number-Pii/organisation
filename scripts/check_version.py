#!/usr/bin/env python3
"""
check_version.py: Number Pii Version Sync Validator

Checks that the version number is consistent across:
  - VERSION
  - CHANGELOG.md (latest heading)
  - CLAUDE.md (protocol version line)
  - GEMINI.md (protocol version line)
  - AGENTS.md (protocol version line)

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
    """Extract latest version heading from CHANGELOG.md (e.g. '## [3.4.0]: ...')."""
    path = REPO_ROOT / "CHANGELOG.md"
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## \[(\d+\.\d+\.\d+)\]", line)
        if m:
            return m.group(1)
    return None


def get_md_protocol_version(filename):
    """Extract protocol version from a context file (_Version: X.Y | ...)."""
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

    # Protocol version (in the context files) is a separate number from the toolkit
    # version, but every generated context file must match CLAUDE.md.
    protocol_sources = {
        "GEMINI.md": get_md_protocol_version("GEMINI.md"),
        "AGENTS.md": get_md_protocol_version("AGENTS.md"),
    }

    errors = []

    # Check toolkit version sync: VERSION vs CHANGELOG
    if changelog and changelog != version_file:
        errors.append(
            f"  VERSION says {version_file}, CHANGELOG.md says {changelog}"
        )

    # Check protocol version sync: each generated file vs CLAUDE.md
    for name, ver in protocol_sources.items():
        if ver != claude_ver:
            errors.append(
                f"  CLAUDE.md protocol version {claude_ver} != {name} protocol version {ver}"
            )

    if errors:
        print("VERSION SYNC FAILED:")
        for e in errors:
            print(e)
        print()
        print(f"  VERSION file:             {version_file}")
        print(f"  CHANGELOG.md latest:      {changelog}")
        print(f"  CLAUDE.md protocol:       {claude_ver}")
        for name, ver in protocol_sources.items():
            print(f"  {name} protocol:       {ver}")
        sys.exit(1)
    else:
        print(f"All versions in sync.")
        print(f"  Toolkit version:          {version_file}")
        print(f"  Protocol version:         {claude_ver}")
        sys.exit(0)


if __name__ == "__main__":
    main()
