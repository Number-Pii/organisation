#!/usr/bin/env python3
"""
check_version.py: Number Pii Version Sync Validator

Checks that the release version is consistent across:
  - VERSION
  - CHANGELOG.md (latest heading)
  - .claude-plugin/plugin.json (plugin manifest, when present)

These three files change only in release PRs (scripts/release.py). Feature
PRs add a changelog fragment under changes/ instead; `--require-fragment`
enforces that in CI so parallel PRs never edit the same version lines.

Exit code 0 = all in sync, 1 = mismatch or missing fragment.

Usage:
    python3 scripts/check_version.py
    python3 scripts/check_version.py --require-fragment origin/main
"""

import argparse
import json
import re
import subprocess
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


def get_plugin_version():
    """Read version from the plugin manifest; None when absent or unreadable."""
    path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("version")
    except (ValueError, OSError):
        return "unparseable"


def changed_files(base: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git diff against {base} failed")
    return [line for line in result.stdout.splitlines() if line.strip()]


def fragment_problem(files: list[str]) -> str:
    """'' when the change set is acceptable, else the reason it is not."""
    if not files:
        return ""
    fragments = [f for f in files
                 if f.startswith("changes/") and f.endswith(".md")
                 and Path(f).name.lower() != "readme.md"]
    is_release = "VERSION" in files
    if is_release or fragments:
        return ""
    return ("no changelog fragment: add changes/<branch-name>.md describing this PR "
            "(see changes/README.md)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check release version consistency")
    parser.add_argument("--require-fragment", metavar="BASE",
                        help="Also fail unless the diff against BASE adds a changes/ "
                             "fragment or is a release (touches VERSION)")
    args = parser.parse_args(argv)

    version_file = get_version_file()
    changelog = get_changelog_version()
    plugin_version = get_plugin_version()

    errors = []
    if changelog and changelog != version_file:
        errors.append(f"  VERSION says {version_file}, CHANGELOG.md says {changelog}")
    if plugin_version is not None and plugin_version != version_file:
        errors.append(
            f"  VERSION says {version_file}, .claude-plugin/plugin.json says {plugin_version}")

    if args.require_fragment:
        try:
            problem = fragment_problem(changed_files(args.require_fragment))
        except RuntimeError as exc:
            problem = f"could not diff against {args.require_fragment}: {exc}"
        if problem:
            errors.append(f"  {problem}")

    if errors:
        print("VERSION CHECK FAILED:")
        for e in errors:
            print(e)
        sys.exit(1)
    print(f"All versions in sync at {version_file}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
