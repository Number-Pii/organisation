#!/usr/bin/env python3
"""
audit_skills.py — Number Pii Skill Coverage Auditor

Reports:
  1. Total skill folders in Teams/skills/
  2. Unique @skill refs currently in Agent Skills sections
  3. Which @skill refs are valid (folder exists) vs broken
  4. Core/Technical skill bullets with and without inline @skill refs
  5. Skills in Teams/skills/ not referenced in any role file
  6. Writes an audit_report.md to scripts/

Usage:
    python scripts/audit_skills.py
    python scripts/audit_skills.py --report          # also write audit_report.md
    python scripts/audit_skills.py --no-color        # plain output (CI / Gemini terminal)
"""

import os
import re
import argparse
from pathlib import Path

# ── Colours (ANSI) ────────────────────────────────────────────────────────────
USE_COLOR = True

def c(text, code): return f"\033[{code}m{text}\033[0m" if USE_COLOR else text
def green(t):  return c(t, "32")
def yellow(t): return c(t, "33")
def red(t):    return c(t, "31")
def bold(t):   return c(t, "1")
def cyan(t):   return c(t, "36")

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
TEAMS_DIR   = REPO_ROOT / "Teams"
SKILLS_DIR  = TEAMS_DIR / "skills"
DEPT_DIRS   = ["01-Executive-Leadership", "02-Engineering", "03-Product-Design",
               "04-Sales-Consultancy", "05-Growth-Marketing", "06-Operations"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_skill_folders():
    """Return a set of all folder names inside Teams/skills/ (excluding non-skill items)."""
    ignore = {".gitignore", "README.md", "SPDD", "workflow_bundles_readme.md"}
    return {
        p.name for p in SKILLS_DIR.iterdir()
        if p.is_dir() and p.name not in ignore
    }


def get_role_files():
    """Return list of (dept, Path) for every .md role file across all departments."""
    roles = []
    for dept in DEPT_DIRS:
        dept_path = TEAMS_DIR / dept
        if dept_path.exists():
            for md in sorted(dept_path.glob("*.md")):
                roles.append((dept, md))
    return roles


def parse_role_file(path: Path):
    """
    Parse a role file and return a dict with:
      - agent_skills: list of @skill-name strings from ## Agent Skills
      - core_bullets: list of (raw_line, has_skill_ref) from ## Core Skills
      - tech_bullets:  list of (raw_line, has_skill_ref) from ## Technical Skills
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    SKILL_RE = re.compile(r"@([a-z0-9][a-z0-9\-]*)")

    agent_skills = []
    core_bullets = []
    tech_bullets = []

    section = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## Agent Skills"):
            section = "agent"
            continue
        elif stripped.startswith("## Core Skills"):
            section = "core"
            continue
        elif stripped.startswith("## Technical Skills"):
            section = "tech"
            continue
        elif stripped.startswith("##"):
            section = None
            continue

        if section == "agent" and stripped.startswith("-"):
            refs = SKILL_RE.findall(stripped)
            agent_skills.extend(refs)

        elif section == "core" and stripped.startswith("-"):
            refs = SKILL_RE.findall(stripped)
            core_bullets.append((stripped, bool(refs)))

        elif section == "tech" and stripped.startswith("-"):
            refs = SKILL_RE.findall(stripped)
            tech_bullets.append((stripped, bool(refs)))

    return {
        "agent_skills": agent_skills,
        "core_bullets": core_bullets,
        "tech_bullets":  tech_bullets,
    }


# ── Main audit ────────────────────────────────────────────────────────────────

def run_audit(write_report=False):
    skill_folders  = get_skill_folders()
    role_files     = get_role_files()

    all_agent_refs     = set()
    broken_agent_refs  = set()
    all_role_refs      = set()   # every @skill seen anywhere in any role

    total_core_bullets = 0
    total_tech_bullets = 0
    linked_core        = 0
    linked_tech        = 0

    role_details = []  # (dept, name, agent_skills, core_bullets, tech_bullets)

    for dept, path in role_files:
        parsed = parse_role_file(path)
        agent  = parsed["agent_skills"]
        core   = parsed["core_bullets"]
        tech   = parsed["tech_bullets"]

        all_agent_refs.update(agent)
        all_role_refs.update(agent)

        # collect inline refs from core/tech bullets too
        SKILL_RE = re.compile(r"@([a-z0-9][a-z0-9\-]*)")
        for line, has_ref in core:
            refs = SKILL_RE.findall(line)
            all_role_refs.update(refs)
        for line, has_ref in tech:
            refs = SKILL_RE.findall(line)
            all_role_refs.update(refs)

        total_core_bullets += len(core)
        total_tech_bullets += len(tech)
        linked_core += sum(1 for _, has in core if has)
        linked_tech += sum(1 for _, has in tech if has)

        role_details.append((dept, path.name, agent, core, tech))

    # Broken agent refs = @skill that has no matching folder
    for ref in all_agent_refs:
        if ref not in skill_folders:
            broken_agent_refs.add(ref)

    unlinked_in_core_tech = total_core_bullets + total_tech_bullets - linked_core - linked_tech
    unlinked_skills       = skill_folders - all_role_refs   # skills nobody references anywhere

    # ── Print report ──────────────────────────────────────────────────────────
    lines_out = []

    def p(line=""):
        print(line)
        lines_out.append(re.sub(r"\033\[\d+m", "", line))   # strip ANSI for file

    p(bold("═" * 65))
    p(bold("  Number Pii — Skill Coverage Audit"))
    p(bold("═" * 65))
    p()

    p(bold("OVERVIEW"))
    p(f"  Total skill folders in Teams/skills/      : {bold(str(len(skill_folders)))}")
    p(f"  Role files scanned                        : {bold(str(len(role_files)))}")
    p(f"  Unique @skill refs in Agent Skills        : {bold(str(len(all_agent_refs)))}")
    p(f"  Broken @skill refs (no matching folder)   : {red(str(len(broken_agent_refs))) if broken_agent_refs else green('0')}")
    p()

    total_bullets = total_core_bullets + total_tech_bullets
    total_linked  = linked_core + linked_tech
    pct = round(100 * total_linked / total_bullets) if total_bullets else 0

    p(bold("CORE + TECHNICAL SKILL BULLET COVERAGE"))
    p(f"  Total Core Skill bullets                  : {total_core_bullets}")
    p(f"  Total Technical Skill bullets             : {total_tech_bullets}")
    p(f"  Total bullets                             : {total_bullets}")
    p(f"  Bullets WITH inline @skill refs           : {green(str(total_linked))}")
    p(f"  Bullets WITHOUT inline @skill refs        : {yellow(str(unlinked_in_core_tech))}")
    p(f"  Coverage                                  : {green(str(pct) + '%') if pct >= 80 else yellow(str(pct) + '%')}")
    p()

    p(bold("UNLINKED SKILLS (not referenced in any role)"))
    p(f"  Skills in Teams/skills/ referenced        : {len(skill_folders) - len(unlinked_skills)}")
    p(f"  Skills in Teams/skills/ NOT referenced    : {yellow(str(len(unlinked_skills)))}")
    p(f"  (Many are highly specialised — Azure SDKs, health tools, etc.)")
    p()

    if broken_agent_refs:
        p(red(bold("BROKEN @SKILL REFS (fix these)")))
        for ref in sorted(broken_agent_refs):
            p(f"  {red('✗')} @{ref}")
        p()

    p(bold("PER-ROLE SUMMARY"))
    p(f"  {'Role':<55} {'Agent':>5}  {'Core':>5}  {'Tech':>5}  {'Inline':>6}")
    p("  " + "─" * 83)
    for dept, name, agent, core, tech in role_details:
        core_linked = sum(1 for _, h in core if h)
        tech_linked = sum(1 for _, h in tech if h)
        total_role  = len(core) + len(tech)
        role_linked = core_linked + tech_linked
        status = green("✓") if role_linked == total_role else (
                 yellow("~") if role_linked > 0 else red("✗"))
        label = name.replace(".md", "")
        p(f"  {status} {label:<53} {str(len(agent)):>5}  {str(core_linked)+'/'+str(len(core)):>5}  "
          f"{str(tech_linked)+'/'+str(len(tech)):>5}  {str(role_linked)+'/'+str(total_role):>6}")
    p()

    p(bold("LEGEND"))
    p(f"  {green('✓')} All Core/Tech bullets have inline @skill refs")
    p(f"  {yellow('~')} Some Core/Tech bullets have inline @skill refs")
    p(f"  {red('✗')} No Core/Tech bullets have inline @skill refs yet")
    p()
    p(bold("─" * 65))
    p(f"  Run this script again after updating role files to track progress.")
    p(bold("─" * 65))

    # ── Write report file ─────────────────────────────────────────────────────
    if write_report:
        report_path = Path(__file__).parent / "audit_report.md"
        report_content = "\n".join(lines_out)
        report_path.write_text(f"# Skill Coverage Audit Report\n\n```\n{report_content}\n```\n",
                               encoding="utf-8")
        print(f"\n{green('✓')} Report written to: {report_path}")

    return {
        "total_skills":        len(skill_folders),
        "total_roles":         len(role_files),
        "agent_refs":          len(all_agent_refs),
        "broken_refs":         sorted(broken_agent_refs),
        "total_bullets":       total_bullets,
        "linked_bullets":      total_linked,
        "unlinked_bullets":    unlinked_in_core_tech,
        "unlinked_skills":     len(unlinked_skills),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit skill coverage in Number Pii role files")
    parser.add_argument("--report",   action="store_true", help="Write audit_report.md to scripts/")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colour output")
    args = parser.parse_args()

    if args.no_color:
        USE_COLOR = False

    run_audit(write_report=args.report)
