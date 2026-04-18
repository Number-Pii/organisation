#!/usr/bin/env python3
"""
find_skill.py — scoped skill search for the Number Pii toolkit.

Searches `Teams/skills/CATEGORIES.md` (with a filesystem fallback) and prints
matching skill names only — without loading any full `SKILL.md`. The AI
assistant picks the right skill from the short result list before spending
tokens to load its full definition.

When a skill carries extended frontmatter (opt-in; see
`scripts/generate_skill_frontmatter.py`), the `domain` field overrides
CATEGORIES.md in the result display and the `summary` field is surfaced
inline. Frontmatter is read only for skills already in the result set, so
queries stay cheap.

Usage:
    python3 scripts/find_skill.py <keyword>               # match keyword across all domains
    python3 scripts/find_skill.py --domain <name>         # list every skill in a domain
    python3 scripts/find_skill.py --domain <name> <kw>    # keyword filtered to one domain
    python3 scripts/find_skill.py --list-domains          # print the domain index

Arguments:
    keyword          Case-insensitive substring matched against skill folder names
    --domain, -d     Restrict results to a domain (case-insensitive partial match)
    --list-domains   Print every domain in CATEGORIES.md and exit
    --names-only     Output skill names only (no domain/summary suffix); useful for piping

Examples:
    python3 scripts/find_skill.py testing
    python3 scripts/find_skill.py --domain security
    python3 scripts/find_skill.py --domain "ai & machine learning" rag
    python3 scripts/find_skill.py --names-only react | head
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_skills import parse_frontmatter  # noqa: E402

ROOT = HERE.parent
SKILLS_DIR = ROOT / "Teams" / "skills"
CATEGORIES_FILE = SKILLS_DIR / "CATEGORIES.md"
SKILL_TOKEN = re.compile(r"`([a-z0-9][a-z0-9\-]*)`")

UNCATEGORISED = "uncategorised"


def parse_categories(path: Path) -> dict[str, list[str]]:
    """Parse CATEGORIES.md into {domain: [skill_name, ...]}."""
    if not path.exists():
        return {}

    domains: dict[str, list[str]] = {}
    current: str | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            if current:
                domains.setdefault(current, [])
            continue
        if current and "`" in line:
            domains[current].extend(SKILL_TOKEN.findall(line))

    return domains


def list_skill_folders(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        return []
    return sorted(
        p.name for p in skills_dir.iterdir()
        if p.is_dir() and not p.name.startswith((".", "_"))
    )


def build_index(
    domains: dict[str, list[str]], folders: list[str]
) -> dict[str, str]:
    """Map skill name -> domain. Folders not in any domain fall back to 'uncategorised'."""
    index: dict[str, str] = {}
    for domain, skills in domains.items():
        for name in skills:
            index.setdefault(name, domain)
    for name in folders:
        index.setdefault(name, UNCATEGORISED)
    return index


def match_domains(query: str, available: list[str]) -> list[str]:
    q = query.lower().strip()
    return [d for d in available if q in d.lower()]


def enrich_from_frontmatter(skill: str) -> tuple[str | None, str | None]:
    """Return (domain, summary) from a skill's frontmatter, or (None, None).

    Only fields that are non-empty strings are returned — callers use CATEGORIES.md
    and name-only formatting as the respective fallbacks.
    """
    skill_md = SKILLS_DIR / skill / "SKILL.md"
    if not skill_md.exists():
        return None, None
    fm, _ = parse_frontmatter(skill_md)
    domain = fm.get("domain") if isinstance(fm.get("domain"), str) and fm.get("domain").strip() else None
    summary = fm.get("summary") if isinstance(fm.get("summary"), str) and fm.get("summary").strip() else None
    return domain, summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search skills without loading any SKILL.md.",
        epilog="Reads Teams/skills/CATEGORIES.md; falls back to folder listing.",
    )
    parser.add_argument("keyword", nargs="?", help="Substring to match in skill names")
    parser.add_argument("--domain", "-d", help="Restrict to a domain (partial match)")
    parser.add_argument(
        "--list-domains", action="store_true", help="List all domains and exit"
    )
    parser.add_argument(
        "--names-only",
        action="store_true",
        help="Print skill names only (no domain suffix)",
    )
    args = parser.parse_args()

    domains = parse_categories(CATEGORIES_FILE)
    folders = list_skill_folders(SKILLS_DIR)
    index = build_index(domains, folders)

    if args.list_domains:
        if not domains:
            print(
                f"No domains parsed. Check that {CATEGORIES_FILE} exists.",
                file=sys.stderr,
            )
            return 1
        for name in sorted(domains):
            print(f"{name}  ({len(set(domains[name]))} skills)")
        return 0

    if args.domain:
        matched = match_domains(args.domain, list(domains.keys()))
        if not matched:
            print(
                f"No domain matched '{args.domain}'. Try --list-domains.",
                file=sys.stderr,
            )
            return 1
        candidates = {skill: d for d in matched for skill in domains[d]}
    else:
        candidates = dict(index)

    if args.keyword:
        q = args.keyword.lower().strip()
        candidates = {s: d for s, d in candidates.items() if q in s.lower()}

    if not candidates:
        print("No matches.", file=sys.stderr)
        return 1

    for skill in sorted(candidates):
        if args.names_only:
            print(skill)
            continue
        fm_domain, fm_summary = enrich_from_frontmatter(skill)
        domain = fm_domain or candidates[skill]
        if fm_summary:
            print(f"{skill}  [{domain}]  — {fm_summary}")
        else:
            print(f"{skill}  [{domain}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
