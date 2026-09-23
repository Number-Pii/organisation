#!/usr/bin/env python3
"""
sync_context.py: Number Pii Managed Block Sync

A consuming project's root AGENTS.md has two parts: the project's own text,
which the toolkit never rewrites, and the toolkit's block between
`<!-- np:begin -->` and `<!-- np:end -->`. This script replaces that block
with the current templates/agents-block.md and nothing else. It writes only
when the bytes differ, carries no version or date, and never runs on its own:
someone runs it after updating the toolkit.

A file without the markers is refused. Pass --append to add the block to the
end of a hand-written file without touching anything already in it.

Usage (from the consuming project root):
    python3 organisation/scripts/sync_context.py            # refresh AGENTS.md
    python3 organisation/scripts/sync_context.py --check    # exit 1 if stale
    python3 organisation/scripts/sync_context.py --append   # add the block to a hand-written file
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.files import write_if_changed  # noqa: E402

TOOLKIT = Path(__file__).resolve().parent.parent
BLOCK_TEMPLATE = TOOLKIT / "templates" / "agents-block.md"
BLOCK_RE = re.compile(r"<!-- np:begin -->.*?<!-- np:end -->\n?", re.DOTALL)


def current_block() -> str:
    block = BLOCK_TEMPLATE.read_text(encoding="utf-8")
    return block if block.endswith("\n") else block + "\n"


def refreshed(text: str, block: str) -> str | None:
    """The file with its managed block replaced; None if it has no block."""
    matches = list(BLOCK_RE.finditer(text))
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError("more than one np:begin/np:end block; keep exactly one")
    m = matches[0]
    return text[:m.start()] + block + text[m.end():]


def appended(text: str, block: str) -> str:
    return text.rstrip("\n") + "\n\n" + block


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the toolkit's managed block in AGENTS.md")
    parser.add_argument("--file", default="AGENTS.md", help="Target file (default: AGENTS.md)")
    parser.add_argument("--check", action="store_true", help="Report staleness, write nothing")
    parser.add_argument("--append", action="store_true",
                        help="Add the block to the end of a file that has none")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: {path} not found. New projects get it from init_project.py.")
        return 1
    text = path.read_text(encoding="utf-8")
    block = current_block()
    try:
        updated = refreshed(text, block)
    except ValueError as exc:
        print(f"ERROR: {path}: {exc}")
        return 1

    if updated is None:
        if not args.append:
            print(f"{path} has no <!-- np:begin --> block, so it was left alone.")
            print("  Pre-4.0 generated pointer: run organisation/scripts/migrate_consumer.py.")
            print("  Hand-written file: re-run with --append to add the block at the end,")
            print("  leaving every existing line as it is.")
            return 1
        updated = appended(text, block)

    if args.check:
        if updated != text:
            print(f"STALE: {path} (run: python3 organisation/scripts/sync_context.py)")
            return 1
        print(f"OK: {path} carries the current toolkit block.")
        return 0

    if write_if_changed(path, updated):
        print(f"Updated the toolkit block in {path}; review the diff and commit it.")
    else:
        print(f"{path} already carries the current toolkit block.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
