#!/usr/bin/env python3
"""
sync_ai_context.py: Generate GEMINI.md and AGENTS.md from CLAUDE.md.

CLAUDE.md is the source of truth. Both files are mechanically derived by
substituting the known divergences for each target.

Usage:
    python3 scripts/sync_ai_context.py          # regenerate both targets
    python3 scripts/sync_ai_context.py --check  # exit 1 if either file is out of sync (CI use)

Exit codes:
    0: success (wrote, or --check confirmed already in sync)
    1: --check detected drift, or input errors
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "CLAUDE.md"

SOURCE_HEADER = (
    "<!-- SYNC: This file is the SOURCE OF TRUTH. GEMINI.md and AGENTS.md are generated from it.\n"
    "     Never edit GEMINI.md or AGENTS.md by hand — run `python3 scripts/sync_ai_context.py`\n"
    "     after editing this file. CI enforces sync with `--check`. -->"
)

GEMINI_TARGET_HEADER = (
    "<!-- GENERATED FILE — do not edit by hand.\n"
    "     This file is generated from CLAUDE.md by scripts/sync_ai_context.py.\n"
    "     To change its contents, edit CLAUDE.md and re-run the sync script. -->"
)

AGENTS_TARGET_HEADER = (
    "<!-- GENERATED FILE — do not edit by hand.\n"
    "     This file is generated from CLAUDE.md by scripts/sync_ai_context.py.\n"
    "     To change its contents, edit CLAUDE.md and re-run the sync script. -->"
)

# The Initialize Protocol body lives in INITIALIZE.md (model-neutral, shared by all
# three context files), so the only divergence left is the acknowledgement line.
GEMINI_SUBSTITUTIONS: list[tuple[str, str]] = [
    (
        "at session start that you have read `CLAUDE.md`",
        "at session start that you have read `GEMINI.md`",
    ),
]

AGENTS_SUBSTITUTIONS: list[tuple[str, str]] = [
    (
        "at session start that you have read `CLAUDE.md`",
        "at session start that you have read `AGENTS.md`",
    ),
]

# Each entry: (output path, generated-file header, substitutions to apply)
TARGETS: list[tuple[Path, str, list[tuple[str, str]]]] = [
    (REPO_ROOT / "GEMINI.md", GEMINI_TARGET_HEADER, GEMINI_SUBSTITUTIONS),
    (REPO_ROOT / "AGENTS.md", AGENTS_TARGET_HEADER, AGENTS_SUBSTITUTIONS),
]


def render_target(source_text: str, header: str, substitutions: list[tuple[str, str]]) -> str:
    if not source_text.startswith(SOURCE_HEADER):
        raise SystemExit(
            f"ERROR: {SOURCE.name} does not start with the expected SYNC header. "
            "Restore the header before running sync."
        )
    body = source_text[len(SOURCE_HEADER):]
    for needle, replacement in substitutions:
        if needle not in body:
            raise SystemExit(
                f"ERROR: substitution target not found in {SOURCE.name}: {needle!r}. "
                "The sync script is out of date with the source file."
            )
        body = body.replace(needle, replacement)
    return header + body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate GEMINI.md and AGENTS.md from CLAUDE.md"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any generated file would change (for CI / pre-commit).",
    )
    args = parser.parse_args()

    source_text = SOURCE.read_text(encoding="utf-8")
    drift = False

    for target_path, header, substitutions in TARGETS:
        rendered = render_target(source_text, header, substitutions)

        if args.check:
            current = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
            if current == rendered:
                print(f"OK: {target_path.name} is in sync with {SOURCE.name}")
            else:
                print(f"DRIFT: {target_path.name} is out of sync with {SOURCE.name}")
                diff = difflib.unified_diff(
                    current.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile=str(target_path.relative_to(REPO_ROOT)) + " (current)",
                    tofile=str(target_path.relative_to(REPO_ROOT)) + " (expected)",
                    n=2,
                )
                sys.stdout.writelines(diff)
                print("\nRun: python3 scripts/sync_ai_context.py")
                drift = True
        else:
            target_path.write_text(rendered, encoding="utf-8")
            print(f"Wrote {target_path.relative_to(REPO_ROOT)} ({len(rendered)} bytes)")

    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
