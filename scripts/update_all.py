#!/usr/bin/env python3
"""
update_all.py: Number Pii Toolkit Fan-Out Updater

Updates every consuming project's toolkit clone listed in consumers.json and
reports a version matrix. Each clone updates via its own scripts/update.py, so
pins (.toolkit-pin) are respected per consumer and doc/ files are never touched.

Usage:
    python3 scripts/update_all.py --check   # report versions only, change nothing
    python3 scripts/update_all.py           # update every clone (no per-clone prompt)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONSUMERS_FILE = REPO_ROOT / "consumers.json"


def load_consumers(path: Path = CONSUMERS_FILE) -> list[dict]:
    """Return [{name, clone: Path}] from the registry; exits with a clear
    message when the registry is missing or malformed."""
    if not path.exists():
        sys.exit(f"ERROR: {path} not found; the consumer registry ships at the toolkit root.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        base = Path(data["base"])
        consumers = data["consumers"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        sys.exit(f"ERROR: {path} is malformed ({exc}).")
    return [
        {"name": c["name"], "clone": base / c["path"] / "organisation"}
        for c in consumers
    ]


def clone_version(clone: Path) -> str:
    version_file = clone / "VERSION"
    if not version_file.exists():
        return ""
    return version_file.read_text(encoding="utf-8").strip()


def clone_pin(clone: Path) -> str:
    for candidate in (clone.parent / ".toolkit-pin", clone / ".toolkit-pin"):
        if candidate.exists():
            ref = candidate.read_text(encoding="utf-8").strip()
            if ref:
                return ref
    return ""


def update_clone(clone: Path) -> bool:
    result = subprocess.run(
        [sys.executable, str(clone / "scripts" / "update.py"), "--yes"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Update every consuming project's toolkit clone")
    parser.add_argument("--check", action="store_true",
                        help="Report the version matrix without updating anything")
    args = parser.parse_args()

    toolkit_version = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    consumers = load_consumers()

    rows = []
    failures = 0
    for consumer in consumers:
        clone = consumer["clone"]
        before = clone_version(clone)
        pin = clone_pin(clone)
        if not before:
            rows.append((consumer["name"], "missing", "missing", pin, "no clone found"))
            failures += 1
            continue
        if args.check:
            status = "pinned" if pin else ("current" if before == toolkit_version else "behind")
            rows.append((consumer["name"], before, before, pin, status))
            continue
        ok = update_clone(clone)
        after = clone_version(clone)
        if not ok:
            failures += 1
        rows.append((consumer["name"], before, after, pin, "updated" if ok else "FAILED"))

    name_w = max(len(r[0]) for r in rows) if rows else 4
    print(f"\nToolkit version here: {toolkit_version}\n")
    print(f"{'Consumer':<{name_w}}  {'Before':>8}  {'After':>8}  {'Pin':>10}  Status")
    for name, before, after, pin, status in rows:
        print(f"{name:<{name_w}}  {before:>8}  {after:>8}  {pin or '-':>10}  {status}")

    if failures:
        print(f"\n{failures} consumer(s) need attention.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
