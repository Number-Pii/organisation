#!/usr/bin/env python3
"""
sync_ai_context.py — Generate GEMINI.md from CLAUDE.md.

CLAUDE.md is the source of truth. GEMINI.md is mechanically derived by
substituting the three known divergences:

  1. The SYNC header comment
  2. "1. This file (`CLAUDE.md`)" in the acknowledgement list
  3. "Initialize CLAUDE.md and read ..." in Step 7

Usage:
    python3 scripts/sync_ai_context.py          # regenerate GEMINI.md
    python3 scripts/sync_ai_context.py --check  # exit 1 if GEMINI.md is out of sync (CI use)

Exit codes:
    0 — success (wrote, or --check confirmed already in sync)
    1 — --check detected drift, or input errors
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "CLAUDE.md"
TARGET = REPO_ROOT / "GEMINI.md"

SOURCE_HEADER = (
    "<!-- SYNC: This file is the SOURCE OF TRUTH. GEMINI.md is generated from it.\n"
    "     Never edit GEMINI.md by hand — run `python3 scripts/sync_ai_context.py`\n"
    "     after editing this file. CI enforces sync with `--check`. -->"
)

TARGET_HEADER = (
    "<!-- GENERATED FILE — do not edit by hand.\n"
    "     This file is generated from CLAUDE.md by scripts/sync_ai_context.py.\n"
    "     To change its contents, edit CLAUDE.md and re-run the sync script. -->"
)

# Exact-string substitutions applied to the remainder of the file.
# Each tuple is (from, to); order matters only if substitutions overlap.
SUBSTITUTIONS: list[tuple[str, str]] = [
    # Acknowledgement list — the filename the assistant confirms it read.
    (
        "at session start that you have read `CLAUDE.md`",
        "at session start that you have read `GEMINI.md`",
    ),
    # Step 7 handover instruction — tool-specific invocation.
    (
        '"Initialize CLAUDE.md and read doc/handover/consolidated_handover.md"',
        '"Initialize GEMINI.md and read doc/handover/consolidated_handover.md"',
    ),
]


def render_target(source_text: str) -> str:
    if not source_text.startswith(SOURCE_HEADER):
        raise SystemExit(
            f"ERROR: {SOURCE.name} does not start with the expected SYNC header. "
            "Restore the header before running sync."
        )
    body = source_text[len(SOURCE_HEADER):]
    for needle, replacement in SUBSTITUTIONS:
        if needle not in body:
            raise SystemExit(
                f"ERROR: substitution target not found in {SOURCE.name}: {needle!r}. "
                "The sync script is out of date with the source file."
            )
        body = body.replace(needle, replacement)
    return TARGET_HEADER + body


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate GEMINI.md from CLAUDE.md")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if GEMINI.md would change (for CI / pre-commit).",
    )
    args = parser.parse_args()

    source_text = SOURCE.read_text(encoding="utf-8")
    rendered = render_target(source_text)

    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current == rendered:
            print(f"OK: {TARGET.name} is in sync with {SOURCE.name}")
            return 0
        print(f"DRIFT: {TARGET.name} is out of sync with {SOURCE.name}")
        diff = difflib.unified_diff(
            current.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile=str(TARGET.relative_to(REPO_ROOT)) + " (current)",
            tofile=str(TARGET.relative_to(REPO_ROOT)) + " (expected)",
            n=2,
        )
        sys.stdout.writelines(diff)
        print("\nRun: python3 scripts/sync_ai_context.py")
        return 1

    TARGET.write_text(rendered, encoding="utf-8")
    print(f"Wrote {TARGET.relative_to(REPO_ROOT)} ({len(rendered)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
