#!/usr/bin/env python3
"""
build_org.py: Number Pii Org Structure Generator

Reads every role file under Teams/ and generates Teams/org.json: departments,
roles, reporting lines, approval authority, and agent skills as machine-readable
data. The markdown role files stay the human view and the source of truth;
org.json is generated output consumed by scripts (and anything else) so no
script hardcodes the org structure.

Usage:
    python3 scripts/build_org.py            # rewrite Teams/org.json
    python3 scripts/build_org.py --check    # exit 1 if org.json is stale (CI)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
TEAMS_DIR = REPO_ROOT / "Teams"
ORG_PATH = TEAMS_DIR / "org.json"

# The only place the department list lives in code; everything else reads org.json.
DEPARTMENTS = [
    ("01-Executive-Leadership", "Executive Leadership"),
    ("02-Engineering", "Engineering"),
    ("03-Product-Design", "Product & Design"),
    ("04-Sales-Consultancy", "Sales & Consultancy"),
    ("05-Growth-Marketing", "Growth & Marketing"),
    ("06-Operations", "Operations"),
]

DETAIL_RE = re.compile(r"^-\s+\*\*(.+?):\*\*\s*(.*)$")
SKILL_RE = re.compile(r"@([a-z0-9][a-z0-9\-]*)")


def parse_role(path: Path, dept_dir: str, dept_name: str) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = next((l[2:].strip() for l in lines if l.startswith("# ")), path.stem)

    details: dict[str, str] = {}
    approval: dict[str, str] = {}
    agent_skills: list[str] = []
    section = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            continue
        m = DETAIL_RE.match(stripped)
        if section == "position details" and m:
            details[m.group(1).strip().lower()] = m.group(2).strip()
        elif section == "approval authority" and m:
            approval[m.group(1).strip().lower()] = m.group(2).strip()
        elif section == "agent skills" and stripped.startswith("-"):
            agent_skills.extend(SKILL_RE.findall(stripped))

    return {
        "title": title,
        "file": str(path.relative_to(REPO_ROOT)),
        "department_dir": dept_dir,
        "department": dept_name,
        "reports_to": details.get("reports to", ""),
        "direct_reports": details.get("direct reports", ""),
        "employment_type": details.get("employment type", ""),
        "can_approve": approval.get("can approve", ""),
        "needs_approval_from": approval.get("needs approval from", ""),
        "agent_skills": sorted(set(agent_skills)),
    }


def collect_org() -> dict:
    roles = []
    for dept_dir, dept_name in DEPARTMENTS:
        dept_path = TEAMS_DIR / dept_dir
        if not dept_path.exists():
            continue
        for md in sorted(dept_path.glob("*.md")):
            roles.append(parse_role(md, dept_dir, dept_name))
    return {
        "departments": [{"dir": d, "name": n} for d, n in DEPARTMENTS],
        "roles": roles,
    }


def render(org: dict) -> str:
    return json.dumps(org, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Teams/org.json from role files")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if org.json is out of date (CI mode)")
    args = parser.parse_args()

    output = render(collect_org())

    if args.check:
        if not ORG_PATH.exists() or ORG_PATH.read_text(encoding="utf-8") != output:
            print("STALE: Teams/org.json (run: python3 scripts/build_org.py)")
            return 1
        print("OK: Teams/org.json matches the role files.")
        return 0

    ORG_PATH.write_text(output, encoding="utf-8")
    org = json.loads(output)
    print(f"Wrote Teams/org.json ({len(org['roles'])} roles, "
          f"{len(org['departments'])} departments)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
