#!/usr/bin/env python3
"""
build_agents.py: Number Pii Role-to-Agent Generator

Generates Claude Code subagent definitions in agents/ from role files under
Teams/. The role markdown stays the source of truth; each agent file is a
generated projection (same pattern as sync_ai_context.py). Regenerate after
editing a source role; CI fails when the two drift.

Only the core delivery roles are generated for now; add a role to CORE_ROLES
once it earns regular direct invocation.

Usage:
    python3 scripts/build_agents.py            # rewrite agents/*.md
    python3 scripts/build_agents.py --check    # exit 1 on drift (CI)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
ORG_PATH = REPO_ROOT / "Teams" / "org.json"
AGENTS_DIR = REPO_ROOT / "agents"

# The five most-invoked delivery roles; the founders decide additions.
CORE_ROLES = [
    "Lead Backend Engineer",
    "Lead Frontend Engineer",
    "Senior Product Manager",
    "QA Automation Engineer",
    "Head of Information Security",
]

GOVERNANCE_NOTE = (
    "You are a virtual role in Number Pii's organisation. You hold delegated "
    "execution authority only: the co-founders hold final decision-making "
    "authority on all matters, and any 'approval' you give operates within the "
    "virtual layer, subject to founder override. Follow the toolkit's "
    "Non-Negotiable Standards at all times: security first, consistent "
    "quality, documentation discipline, mandatory context files, version "
    "control discipline (never push to main), and the Writing Style rules."
)


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def load_org() -> dict:
    if not ORG_PATH.exists():
        sys.exit("ERROR: Teams/org.json missing; run scripts/build_org.py first.")
    return json.loads(ORG_PATH.read_text(encoding="utf-8"))


def role_sections(role_file: Path) -> dict[str, str]:
    """Split a role file into {lower-cased h2 heading: body text}."""
    sections: dict[str, str] = {}
    current = None
    body: list[str] = []
    for line in role_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(body).strip()
            current = line[3:].strip().lower()
            body = []
        elif current:
            body.append(line)
    if current:
        sections[current] = "\n".join(body).strip()
    return sections


def render_agent(role: dict) -> str:
    source = REPO_ROOT / role["file"]
    sections = role_sections(source)
    summary = sections.get("role summary", "").strip()
    first_sentence = re.split(r"(?<=[.!?])\s+", summary)[0] if summary else role["title"]

    lines = [
        "---",
        f"name: np-{slugify(role['title'])}",
        f"description: {first_sentence} Invoke for work this role owns; "
        f"generated from {role['file']}.",
        "---",
        "",
        f"# {role['title']} (Number Pii)",
        "",
        GOVERNANCE_NOTE,
        "",
        "## Role",
        summary or "[see source role file]",
        "",
        "## Core Skills",
        sections.get("core skills", "- [see source role file]"),
    ]
    tech = sections.get("technical skills", "").strip()
    if tech:
        lines += ["", "## Technical Skills", tech]
    lines += [
        "",
        "## Authority Boundaries",
        f"- Can approve (virtual layer only): {role['can_approve'] or 'nothing recorded'}",
        f"- Needs approval from: {role['needs_approval_from'] or 'nothing recorded'}",
        f"- Reports to: {role['reports_to'] or 'unrecorded'}",
        "",
        "## Skills to Invoke",
        sections.get("agent skills", "- [see source role file]"),
        "",
        f"_Generated from {role['file']} by scripts/build_agents.py; edit the "
        "role file, then regenerate._",
        "",
    ]
    return "\n".join(lines)


def build_all() -> dict[Path, str]:
    org = load_org()
    by_title = {r["title"]: r for r in org["roles"]}
    files: dict[Path, str] = {}
    missing = [t for t in CORE_ROLES if t not in by_title]
    if missing:
        sys.exit(f"ERROR: CORE_ROLES not found in org.json: {', '.join(missing)}")
    for title in CORE_ROLES:
        role = by_title[title]
        files[AGENTS_DIR / f"np-{slugify(title)}.md"] = render_agent(role)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate agents/*.md from role files")
    parser.add_argument("--check", action="store_true", help="Exit 1 on drift (CI mode)")
    args = parser.parse_args()

    files = build_all()

    if args.check:
        stale = [str(p.relative_to(REPO_ROOT)) for p, content in files.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != content]
        expected = {p.name for p in files}
        strays = [f.name for f in AGENTS_DIR.glob("np-*.md")
                  if f.name not in expected] if AGENTS_DIR.exists() else []
        if stale or strays:
            for s in stale:
                print(f"STALE: {s}")
            for s in strays:
                print(f"STRAY: agents/{s} (no matching CORE_ROLES entry)")
            print("Run: python3 scripts/build_agents.py")
            return 1
        print(f"OK: {len(files)} agent definitions match their role files.")
        return 0

    AGENTS_DIR.mkdir(exist_ok=True)
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
