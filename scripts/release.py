#!/usr/bin/env python3
"""
release.py: Number Pii Toolkit Release Builder

Compiles the changelog fragments in changes/ into a new CHANGELOG.md section,
bumps VERSION and .claude-plugin/plugin.json, and deletes the fragments.

Feature PRs never touch VERSION or CHANGELOG.md; each adds one fragment file
named after its branch, so parallel PRs cannot conflict. A release is its own
PR (branch `chore/release-X.Y.Z`) that runs this script.

Fragment format (changes/<branch-slug>.md):

    ---
    bump: minor          # major | minor | patch (default patch)
    section: Added       # default heading for bullets before any ### heading
    ---
    - **Thing.** What changed and why.

    ### Fixed
    - Bullets under a ### heading go to that section instead.

Usage:
    python3 scripts/release.py --dry-run        # preview the section and version
    python3 scripts/release.py                  # write the release
    python3 scripts/release.py --version 4.0.0  # override the computed version
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.frontmatter import parse_frontmatter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
BUMPS = ("patch", "minor", "major")
SECTION_ORDER = ["Breaking", "Added", "Changed", "Fixed", "Removed",
                 "Deprecated", "Security", "Migration"]
HEADING = re.compile(r"^### +(.+?)\s*$")


def fragment_files(root: Path) -> list[Path]:
    changes = root / "changes"
    if not changes.is_dir():
        return []
    return sorted(p for p in changes.glob("*.md") if p.name.lower() != "readme.md")


def read_fragment(path: Path) -> tuple[str, dict[str, list[str]]]:
    """Return (bump, {section: [lines]}) for one fragment."""
    fm, _ = parse_frontmatter(path)
    bump = _value(fm, "bump", "patch").lower()
    if bump not in BUMPS:
        raise ValueError(f"{path.name}: bump must be one of {', '.join(BUMPS)}, got '{bump}'")
    section = _value(fm, "section", "Changed")

    text = path.read_text(encoding="utf-8")
    body = text.split("\n")
    if fm and body and body[0].strip() == "---":
        end = next(i for i in range(1, len(body)) if body[i].strip() == "---")
        body = body[end + 1:]

    sections: dict[str, list[str]] = {}
    current = section
    for line in body:
        m = HEADING.match(line)
        if m:
            current = m.group(1)
            continue
        sections.setdefault(current, []).append(line.rstrip())
    cleaned = {k: _trim(v) for k, v in sections.items()}
    return bump, {k: v for k, v in cleaned.items() if v}


def _value(fm: dict, key: str, default: str) -> str:
    """A frontmatter scalar with any trailing `# comment` removed."""
    return str(fm.get(key, default)).split("#", 1)[0].strip() or default


def _trim(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def next_version(current: str, bump: str) -> str:
    major, minor, patch = (int(x) for x in current.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def render_section(version: str, date: str, merged: dict[str, list[list[str]]]) -> str:
    ordered = [s for s in SECTION_ORDER if s in merged]
    ordered += sorted(s for s in merged if s not in SECTION_ORDER)
    out = [f"## [{version}]: {date}", ""]
    for name in ordered:
        out.append(f"### {name}")
        for block in merged[name]:
            out.extend(block)
        out.append("")
    return "\n".join(out) + "\n"


def insert_section(changelog: str, section: str) -> str:
    """Insert before the first existing '## [' heading (after the preamble)."""
    m = re.search(r"^## \[", changelog, flags=re.M)
    if not m:
        return changelog.rstrip("\n") + "\n\n" + section
    return changelog[:m.start()] + section + changelog[m.start():]


def build_release(root: Path, version: str | None, date: str):
    files = fragment_files(root)
    if not files:
        raise ValueError("no changelog fragments in changes/; nothing to release")
    bump_rank = 0
    merged: dict[str, list[list[str]]] = {}
    for path in files:
        bump, sections = read_fragment(path)
        bump_rank = max(bump_rank, BUMPS.index(bump))
        for name, lines in sections.items():
            merged.setdefault(name, []).append(lines)
    current = (root / "VERSION").read_text(encoding="utf-8").strip()
    new = version or next_version(current, BUMPS[bump_rank])
    return current, new, files, render_section(new, date, merged)


def write_release(root: Path, new: str, files: list[Path], section: str) -> None:
    changelog = root / "CHANGELOG.md"
    changelog.write_text(insert_section(changelog.read_text(encoding="utf-8"), section),
                         encoding="utf-8")
    (root / "VERSION").write_text(new + "\n", encoding="utf-8")
    plugin = root / ".claude-plugin" / "plugin.json"
    if plugin.exists():
        text = plugin.read_text(encoding="utf-8")
        data = json.loads(text)
        if data.get("version") != new:
            text = re.sub(r'("version"\s*:\s*")[^"]*(")', rf"\g<1>{new}\g<2>", text, count=1)
            plugin.write_text(text, encoding="utf-8")
    for path in files:
        path.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile changes/ fragments into a release")
    parser.add_argument("--dry-run", action="store_true", help="Print the result, write nothing")
    parser.add_argument("--version", help="Release this exact version instead of the computed one")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        current, new, files, section = build_release(REPO_ROOT, args.version, args.date)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"{current} -> {new} from {len(files)} fragment(s)")
    if args.dry_run:
        print()
        print(section)
        return 0
    write_release(REPO_ROOT, new, files, section)
    print(f"Wrote CHANGELOG.md, VERSION and plugin.json; removed {len(files)} fragment(s).")
    print(f"Commit on a chore/release-{new} branch and open the release PR.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
