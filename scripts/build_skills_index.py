#!/usr/bin/env python3
"""
build_skills_index.py: Number Pii Skills Index Generator

Reads the frontmatter of every SKILL.md under Teams/skills/ and generates:
  1. Teams/skills/skills-index.json  (machine-readable; consumed by find_skill.py)
  2. Teams/skills/CATEGORIES.md      (human-readable view, grouped by domain)

Both files are generated output; edit skill frontmatter, never these files.
Domain descriptions are carried over from the existing CATEGORIES.md, so a new
domain needs its description line added once by hand after generation flags it.

Usage:
    python3 scripts/build_skills_index.py            # rewrite both files
    python3 scripts/build_skills_index.py --check    # exit 1 if either is stale (CI)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lib.frontmatter import parse_frontmatter  # noqa: E402

REPO_ROOT = HERE.parent
SKILLS_DIR = REPO_ROOT / "Teams" / "skills"
INDEX_PATH = SKILLS_DIR / "skills-index.json"
CATEGORIES_PATH = SKILLS_DIR / "CATEGORIES.md"

NON_SKILL_ITEMS = {"SPDD"}
TIERS = ("curated", "standard", "archive")
UNCATEGORISED = "uncategorised"

CATEGORIES_HEADER = """# Skills by Category

> GENERATED FILE: rebuild with `python3 scripts/build_skills_index.py`.
> Grouping, tiers, and summaries come from each skill's SKILL.md frontmatter.
> {total} skills: {curated} curated, {standard} standard, {archived} archived.
> Canonical skills are marked (canonical) and listed first in their domain.
> Search without loading files: `python3 scripts/find_skill.py <keyword>`.
"""


def collect_skills() -> list[dict]:
    skills = []
    for folder in sorted(SKILLS_DIR.iterdir()):
        if not folder.is_dir() or folder.name in NON_SKILL_ITEMS or folder.name.startswith("."):
            continue
        fm, line_count = parse_frontmatter(folder / "SKILL.md")
        tier = fm.get("tier") if fm.get("tier") in TIERS else "standard"
        domain = fm.get("domain") if isinstance(fm.get("domain"), str) and fm.get("domain").strip() else UNCATEGORISED
        summary = fm.get("summary") if isinstance(fm.get("summary"), str) else ""
        skills.append({
            "name": folder.name,
            "domain": domain,
            "summary": summary,
            "size_class": fm.get("size_class") if isinstance(fm.get("size_class"), str) else "",
            "risk": fm.get("risk") if isinstance(fm.get("risk"), str) else "",
            "source": fm.get("source") if isinstance(fm.get("source"), str) else "",
            "tier": tier,
            "canonical": fm.get("canonical") == "true",
            "lines": line_count,
        })
    return skills


def render_index(skills: list[dict]) -> str:
    return json.dumps({"skills": skills}, indent=2, ensure_ascii=False) + "\n"


def existing_domain_descriptions() -> dict[str, str]:
    """Carry the one-line domain descriptions over from the current CATEGORIES.md."""
    descriptions: dict[str, str] = {}
    if not CATEGORIES_PATH.exists():
        return descriptions
    current = None
    for line in CATEGORIES_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if current and line.strip() and not line.startswith(("`", ">", "#", "-")):
            descriptions.setdefault(current, line.strip())
            current = None
    return descriptions


def sort_key(skill: dict):
    tier_rank = {"curated": 1, "standard": 2, "archive": 3}
    return (0 if skill["canonical"] else 1, tier_rank[skill["tier"]], skill["name"])


def render_categories(skills: list[dict]) -> str:
    descriptions = existing_domain_descriptions()
    active = [s for s in skills if s["tier"] != "archive"]
    archived = [s for s in skills if s["tier"] == "archive"]

    counts = {
        "total": len(skills),
        "curated": sum(1 for s in skills if s["tier"] == "curated"),
        "standard": sum(1 for s in skills if s["tier"] == "standard"),
        "archived": len(archived),
    }
    out = [CATEGORIES_HEADER.format(**counts), "---", ""]

    domains: dict[str, list[dict]] = {}
    for s in active:
        domains.setdefault(s["domain"], []).append(s)

    for domain in sorted(domains, key=str.lower):
        out.append(f"## {domain}")
        desc = descriptions.get(domain, "[FILL IN: one-line domain description]")
        out.append(desc)
        out.append("")
        names = []
        for s in sorted(domains[domain], key=sort_key):
            label = f"`{s['name']}`"
            if s["canonical"]:
                label += " (canonical)"
            names.append(label)
        out.append(" · ".join(names))
        out.append("")
        out.append("---")
        out.append("")

    out.append("## Archived")
    out.append("Off-charter or superseded skills, kept for reference; excluded from default search.")
    out.append("")
    out.append(" · ".join(f"`{s['name']}`" for s in sorted(archived, key=sort_key)))
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate skills-index.json and CATEGORIES.md from skill frontmatter")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if either generated file is out of date (CI mode)")
    args = parser.parse_args()

    skills = collect_skills()
    index = render_index(skills)
    categories = render_categories(skills)

    def display(path: Path) -> str:
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return str(path)

    if args.check:
        stale = []
        if not INDEX_PATH.exists() or INDEX_PATH.read_text(encoding="utf-8") != index:
            stale.append(display(INDEX_PATH))
        if not CATEGORIES_PATH.exists() or CATEGORIES_PATH.read_text(encoding="utf-8") != categories:
            stale.append(display(CATEGORIES_PATH))
        if stale:
            print("STALE generated files (run: python3 scripts/build_skills_index.py):")
            for s in stale:
                print(f"  {s}")
            return 1
        print("OK: skills-index.json and CATEGORIES.md match skill frontmatter.")
        return 0

    INDEX_PATH.write_text(index, encoding="utf-8")
    CATEGORIES_PATH.write_text(categories, encoding="utf-8")
    print(f"Wrote {display(INDEX_PATH)} ({len(skills)} skills)")
    print(f"Wrote {display(CATEGORIES_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
