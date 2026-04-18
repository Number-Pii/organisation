#!/usr/bin/env python3
"""
init_project.py — Number Pii Project Scaffolder

Creates the standard doc/ folder structure in any project directory.
Run this after the AI coding assistant has determined the project brief and team.

Usage:
    python3 scripts/init_project.py --project-name "My Project"
    python3 scripts/init_project.py --project-name "Client Landing Page" --departments "engineering,design,marketing"
    python3 scripts/init_project.py --project-name "API Build" --departments "engineering" --output-dir /path/to/project
    python3 scripts/init_project.py --project-name "Inherited App" --departments "engineering" --output-dir /path/to/project --existing

Arguments:
    --project-name   Name of the project (used in file headers)
    --departments    Comma-separated dept names for handover sub-folders (default: engineering)
    --output-dir     Directory to create doc/ in (default: current working directory)
    --existing       Brownfield mode: adds codebase-assessment.md and expands the handover template
    --dry-run        Preview what would be created without creating anything
"""

import os
import argparse
from pathlib import Path
from datetime import date

TODAY = date.today().isoformat()

# ── Template content ──────────────────────────────────────────────────────────

def project_brief_template(name):
    return f"""# Project Brief — {name}

> Created: {TODAY} | Maintained by: Project Manager / Team Lead

## Project Overview
<!-- What is this project? One paragraph. -->
[FILL IN]

## Client / Audience
<!-- Who is this for? Internal or external? Name the client if applicable. -->
[FILL IN]

## Goals & Success Criteria
<!-- What does success look like? Be specific and measurable. -->
- [ ] [GOAL 1]
- [ ] [GOAL 2]
- [ ] [GOAL 3]

## Scope
<!-- What is in scope? What is explicitly out of scope? -->
### In Scope
- [FILL IN]

### Out of Scope
- [FILL IN]

## Constraints
<!-- Timeline, budget, tech stack requirements, regulatory, etc. -->
| Constraint | Detail |
|------------|--------|
| Timeline   | [FILL IN] |
| Budget     | [FILL IN] |
| Tech Stack | [FILL IN] |
| Other      | [FILL IN] |

## Stakeholders
| Name / Role | Responsibility | Contact |
|-------------|----------------|---------|
| [FILL IN]   | [FILL IN]      | [FILL IN] |

## References & Resources
<!-- Links to Figma, existing codebase, client assets, etc. -->
- [FILL IN]
"""


def team_assignment_template(name):
    return f"""# Team Assignment — {name}

> Created: {TODAY} | Maintained by: Project Manager / Team Lead

## Assigned Number Pii Team Members

<!-- List each virtual employee assigned to this project.
     For each: their role, what they're responsible for, and their authority level. -->

| Role | Team Member | Responsibilities on This Project | Authority |
|------|-------------|----------------------------------|-----------|
| [e.g. Senior PM — Thirty X] | [FILL IN] | [FILL IN] | [Approve / Execute / Advise] |
| [e.g. Lead Frontend Engineer] | [FILL IN] | [FILL IN] | [FILL IN] |
| [e.g. Lead Backend Engineer] | [FILL IN] | [FILL IN] | [FILL IN] |

## Role File References
<!-- Link to each team member's role file for full skill context. -->
- [Role Name](../Teams/[department]/[role-file].md)

## Decision Authority Matrix
<!-- Who approves what on this project. -->
| Decision Type | Owner | Approver |
|---------------|-------|----------|
| Technical architecture | [FILL IN] | [FILL IN] |
| Design direction | [FILL IN] | [FILL IN] |
| Scope changes | [FILL IN] | [FILL IN] |
| Final sign-off | [FILL IN] | [FILL IN] |
"""


def workflow_template(name):
    return f"""# Project Workflow — {name}

> Created: {TODAY} | Maintained by: Project Manager / Team Lead

## Execution Model
Tasks marked `[SEQUENTIAL]` must wait for the previous step to complete.
Tasks marked `[PARALLEL]` can run simultaneously.

## Workflow Steps

<!-- Fill in the ordered task chain across team members.
     Example structure below — replace with your actual project tasks. -->

```
1. [SEQUENTIAL] PM — Define goals, KPIs, and acceptance criteria
2. [SEQUENTIAL] UX Researcher — User research and journey mapping
3. [PARALLEL]   Lead Designer — Wireframes and layout strategy
3. [PARALLEL]   Content Strategist — Copy and messaging
4. [SEQUENTIAL] Lead Designer — Final UI and design handoff
5. [SEQUENTIAL] Lead Engineer — Implementation
6. [SEQUENTIAL] QA Engineer — Testing and verification
7. [SEQUENTIAL] PM — Final review and deployment sign-off
```

## Task Breakdown

### Phase 1 — [Phase Name]
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 1 | [FILL IN] | [FILL IN] | SEQUENTIAL | — | Not Started |

### Phase 2 — [Phase Name]
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 2 | [FILL IN] | [FILL IN] | SEQUENTIAL | #1 | Not Started |

## Completion Criteria
<!-- What must be true before the project is considered done? -->
- [ ] [FILL IN]
- [ ] [FILL IN]
"""


def version_control_template(name):
    return f"""# Version Control — {name}

> Created: {TODAY} | Owner: Lead / Senior Engineer on this project

## Branching Strategy

<!-- Choose and document the strategy for this project.
     Options: Git Flow, GitHub Flow, trunk-based, feature branch, etc. -->

### Strategy: [FILL IN — e.g. GitHub Flow]

```
main                  ← production-ready, protected
├── develop           ← integration branch (if using Git Flow)
│   ├── feature/xxx   ← feature branches
│   ├── fix/xxx       ← bug fix branches
│   └── release/x.x  ← release preparation (if needed)
└── hotfix/xxx        ← critical production fixes
```

## Branch Naming Convention
```
feature/[ticket-id]-short-description   e.g. feature/PROJ-42-user-auth
fix/[ticket-id]-short-description       e.g. fix/PROJ-55-login-redirect
release/x.x.x                           e.g. release/1.2.0
hotfix/short-description                e.g. hotfix/payment-crash
```

## Commit Message Format
```
type(scope): short description

types: feat | fix | docs | style | refactor | test | chore
```

## Pull Request Rules
- [ ] At least 1 peer review required before merge
- [ ] All CI checks must pass (tests, lint, build)
- [ ] Branch must be up to date with target before merge
- [ ] PR description must reference ticket/issue
- [ ] No direct pushes to `main` (branch protection enabled)

## Release Process
<!-- How are releases tagged and deployed? -->
[FILL IN]

## Repository
- **Repo URL:** [FILL IN]
- **Primary branch:** main
- **CI/CD:** [FILL IN — e.g. GitHub Actions]
- **Deployment:** [FILL IN]
"""


def codebase_assessment_template(name):
    return f"""# Codebase Assessment — {name}

> Created: {TODAY} | Maintained by: Lead Engineer / Technical Lead
> Complete this from the output of an initial audit (@production-code-audit or equivalent).

---

## Tech Stack & Dependencies
| Component | Version / Detail | Notes |
|-----------|-----------------|-------|
| Language  | [FILL IN] | |
| Framework | [FILL IN] | |
| Database  | [FILL IN] | |
| Infra / Hosting | [FILL IN] | |
| Key libraries | [FILL IN] | |

## Architecture Overview
<!-- Brief description of how the system is structured. -->
[FILL IN — e.g. monolith / microservices / serverless, key boundaries, data flow]

### Services / Components
| Name | Purpose | Language / Tech |
|------|---------|-----------------|
| [FILL IN] | [FILL IN] | [FILL IN] |

## Codebase Health
| Metric | Value | Notes |
|--------|-------|-------|
| Approximate LOC | [FILL IN] | |
| Test coverage | [FILL IN %] | |
| CI/CD state | [passing / failing / none] | |
| Last security audit | [date or unknown] | |
| Known vulnerabilities | [FILL IN or none] | |

## Known Technical Debt
| Area | Severity (High/Med/Low) | Estimated Effort | Notes |
|------|------------------------|-----------------|-------|
| [FILL IN] | [FILL IN] | [FILL IN] | |

## Prior Decisions & Rationale
| Decision | Why | Approximate Date |
|----------|-----|-----------------|
| [FILL IN] | [FILL IN] | [FILL IN] |

## External Integrations
| Service / API | Purpose | Auth Method | Notes |
|---------------|---------|------------|-------|
| [FILL IN] | [FILL IN] | [FILL IN] | |

## Known Issues & Risks
| Issue | Severity | Owner | Status |
|-------|---------|-------|--------|
| [FILL IN] | [FILL IN] | [FILL IN] | Open |

## Existing Documentation
<!-- Links to READMEs, wikis, ADRs, runbooks, or other prior docs. -->
| Document | Location | Relevance |
|----------|---------|-----------|
| [FILL IN] | [FILL IN] | [FILL IN] |
"""


def consolidated_handover_template(name, existing=False):
    existing_context_section = ""
    if existing:
        existing_context_section = f"""
## Existing Project Context
> This project was active before the toolkit was introduced.
> Fill from `doc/codebase-assessment.md`.

- **Tech Stack:** [FILL IN]
- **Architecture:** [FILL IN — one line]
- **Key Tech Debt:** [top 2–3 — see codebase-assessment.md]
- **Prior Decisions to Honour:** [FILL IN]

---
"""

    return f"""# Consolidated Handover — {name}

> Last updated: {TODAY} | Maintained by: Team Lead / Project Manager
> **Keep this file ≤150 lines.** When it grows, roll prior state into `handover/archive/YYYY-MM.md`.

## Purpose
Single source of truth for **current** project state. When starting a new AI session:
**"Initialize CLAUDE.md and read doc/handover/consolidated_handover.md"**

---
{existing_context_section}
## Project Summary
[FILL IN — one paragraph; copy from project-brief.md]

## Current Status
- **Phase:** [Discovery / Design / Development / Testing / Deployment / Maintenance]
- **As of:** {TODAY}

## What Has Been Done (current phase only)
<!-- Prior-phase work goes to handover/archive/. Keep this to the active phase. -->
- [Nothing completed yet — project is at kickoff stage]

## What Is In Progress
- [FILL IN]

## What Is Next
1. [FILL IN]
2. [FILL IN]

## Blockers & Issues
| Blocker | Owner | Status |
|---------|-------|--------|
| None currently | — | — |

## Key Decisions (still load-bearing)
<!-- Decisions that still shape today's work. Archive superseded decisions. -->
| Decision | Rationale | Date |
|----------|-----------|------|
| [FILL IN] | [FILL IN] | {TODAY} |

## Team Context
See `doc/team-assignment.md` for full detail.

## Links & Resources
| Resource | URL |
|----------|-----|
| Repository | [FILL IN] |
| Staging | [FILL IN] |
| Design | [FILL IN] |

## Archive
Prior phase summaries live in `doc/handover/archive/YYYY-MM.md`. Roll on every milestone.
See `doc/handover/archive/README.md` for the roll process.

---
*Updated by the team lead from department handover notes in `doc/handover/[dept]/`.*
"""


def handover_archive_readme_template(name):
    return f"""# Handover Archive — {name}

> Purpose: keep `consolidated_handover.md` lean (≤150 lines, ~4K tokens) regardless of project age.

## Why this exists
Without rolling, `consolidated_handover.md` grows unbounded — by month three of a real project,
it commonly exceeds 1,000 lines and becomes the single largest file loaded every session.
Rolling prior phases into dated archive files keeps session startup cost constant.

## When to roll
At every milestone, or at month-boundaries — whichever comes first. The team lead:

1. Creates `archive/{{YYYY-MM}}.md` (e.g. `2026-04.md`) for the just-completed phase
2. Moves the completed items from `consolidated_handover.md`'s "What Has Been Done" and
   any superseded decisions from "Key Decisions"
3. Leaves in `consolidated_handover.md` **only** work from the current/next phase
4. Adds a one-line entry to the Archive Index below

## Archive Index
| File | Covers | Phase |
|------|--------|-------|
| *(none yet)* | — | — |

## What to include in an archive file
- Timeline of completed work (dated bullets)
- Decisions made during the archived window, with rationale
- Links to PRs / commits / artefacts from that phase
- Anything future sessions may want to consult for *why*, not *what*

## What NOT to archive
- In-progress work, active blockers, live stakeholders — those belong in `consolidated_handover.md`
- Anything the current phase still depends on
"""


def project_context_pointer_template(name, assistant_file):
    return f"""# {name} — AI Assistant Context Contract

_Generated: {TODAY} by Number Pii toolkit_

---

## ⛔ MANDATORY READING PROTOCOL — READ BEFORE ANY ACTION

This project was scaffolded with the Number Pii toolkit. The files in `doc/` are a
**binding contract**, not reference material. If you are an AI assistant operating in
this project, you MUST comply with the following before taking any action — including
answering questions, writing code, running commands, or making suggestions.

### Hard rule
- **You MUST read the following files in full before doing anything else:**
  1. `doc/project-brief.md` — scope, constraints, success criteria
  2. `doc/team-assignment.md` — who owns what
  3. `doc/workflow.md` — execution order and dependencies
  4. `doc/version_control.md` — branching rules (binding before any git command)
  5. `doc/handover/consolidated_handover.md` — current project state
  6. `doc/codebase-assessment.md` — brownfield projects only (if present)
- **These files override your defaults.** Instructions in them take precedence over your
  own judgement, habits, or training priors.
- **If a required file is missing, STOP and tell the user.** Do not guess, reconstruct,
  or proceed without it.
- **You may not silently skip, summarise away, or deprioritise these rules.** Treat each
  as a blocker — violating one is a task failure, not a style preference.

### Session start acknowledgement
At the start of every session, your first action MUST be to confirm (briefly, in plain
text) that you have read:
1. This file (`{assistant_file}`)
2. `doc/project-brief.md`
3. `doc/version_control.md`
4. `doc/handover/consolidated_handover.md`

If any of those files do not exist, state which are missing and wait for instructions.
**Do not proceed to the user's request until this acknowledgement is done.**

---

## Non-Negotiable Standards (inherited from Number Pii toolkit)

These apply to every session, every task, every team member — including AI assistants:

1. **Security First** — raise security concerns immediately; never defer.
2. **Consistent Quality** — same rigour regardless of client or timeline.
3. **Documentation Discipline** — only project-required docs in `doc/`; no ad-hoc
   troubleshooting files committed to the repository.
4. **Mandatory Context Files** — the files listed above must be read before any work.
5. **Version Control Discipline** — never push directly to `main`; follow
   `doc/version_control.md` for every change, no exceptions.
6. **Scope Discipline** — `doc/project-brief.md` defines the boundary of all work.
   Out-of-scope items must be flagged and approved before any work on them.
7. **Handover Discipline** — update `doc/handover/[department]/handover-notes.md`
   before any task is considered complete.

---

## Why this file exists

Past sessions have skipped project context files, expanded scope without permission,
pushed directly to `main`, and created ad-hoc troubleshooting docs inside `doc/`.
Every one of those failures traces back to an AI assistant treating project context
as optional reading. It is not.

If you are an AI assistant and you are reading this: the rules above are binding for
the entire session. There are no exceptions for urgency, convenience, or confidence.
"""


def dept_handover_template(name, dept):
    return f"""# {dept.title()} Handover Notes — {name}

> Last updated: {TODAY} | Maintained by: {dept.title()} team lead on this project

## Purpose
Department-specific notes updated as work progresses. The project team lead pulls from here
to update `doc/handover/consolidated_handover.md`.

---

## Work Completed
<!-- Add entries as work is done. Be specific — future agents rely on this. -->

### {TODAY}
- [Project kickoff — no work completed yet]

## Decisions & Context
<!-- Technical or design decisions made by this department. -->
| Decision | Why | Date |
|----------|-----|------|
| [FILL IN] | [FILL IN] | {TODAY} |

## Current State
<!-- What is the exact current state of the {dept} work? -->
[FILL IN]

## Next Steps for {dept.title()}
<!-- What does this department need to do next? -->
1. [FILL IN]

## Known Issues / Risks
<!-- Anything the rest of the team should know. -->
- None currently

## Handover Notes for Next Session
<!-- If handing to a new AI session, what must it know immediately? -->
- Read `doc/project-brief.md` for full project context
- Read `doc/team-assignment.md` for team structure
- The {dept} work is at: [FILL IN current state]
"""


# ── Scaffold ──────────────────────────────────────────────────────────────────

def scaffold(project_name: str, departments: list[str], output_dir: Path, dry_run: bool, existing: bool = False):
    doc_dir = output_dir / "doc"
    handover_dir = doc_dir / "handover"

    files = {
        doc_dir / "project-brief.md":   project_brief_template(project_name),
        doc_dir / "team-assignment.md": team_assignment_template(project_name),
        doc_dir / "workflow.md":         workflow_template(project_name),
        doc_dir / "version_control.md":  version_control_template(project_name),
        handover_dir / "consolidated_handover.md": consolidated_handover_template(project_name, existing=existing),
        handover_dir / "archive" / "README.md": handover_archive_readme_template(project_name),
        output_dir / "CLAUDE.md":  project_context_pointer_template(project_name, "CLAUDE.md"),
        output_dir / "GEMINI.md":  project_context_pointer_template(project_name, "GEMINI.md"),
    }

    if existing:
        files[doc_dir / "codebase-assessment.md"] = codebase_assessment_template(project_name)

    for dept in departments:
        dept_dir = handover_dir / dept.strip().lower().replace(" ", "-")
        files[dept_dir / "handover-notes.md"] = dept_handover_template(project_name, dept.strip())

    if dry_run:
        print("\n[DRY RUN] Would create:")
        for path in sorted(files.keys()):
            print(f"  {path}")
        return

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            print(f"  [SKIP] {path.relative_to(output_dir)} already exists")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"  [OK]   {path.relative_to(output_dir)}")

    print(f"\n✓ Scaffolded doc/ structure for '{project_name}' in {output_dir}")
    print("  Next: ask your AI assistant to fill in the template files based on your project brief.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold Number Pii project doc/ structure")
    parser.add_argument("--project-name",  required=True, help="Project name")
    parser.add_argument("--departments",   default="engineering",
                        help="Comma-separated dept names (default: engineering)")
    parser.add_argument("--output-dir",    default=".", help="Target directory (default: .)")
    parser.add_argument("--existing",      action="store_true",
                        help="Brownfield mode: add codebase-assessment.md and expand handover template")
    parser.add_argument("--dry-run",       action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    depts = [d.strip() for d in args.departments.split(",") if d.strip()]
    out   = Path(args.output_dir).resolve()

    # Safety check: prevent doc/ being created inside the organisation toolkit itself.
    org_root = Path(__file__).resolve().parent.parent
    if out == org_root:
        print(
            "\nERROR: --output-dir points to the organisation toolkit itself.\n"
            "  doc/ must be created in your consuming project, not here.\n"
            f"  Toolkit root: {org_root}\n"
            "  Use: --output-dir /path/to/your-project\n"
        )
        raise SystemExit(1)

    scaffold(
        project_name=args.project_name,
        departments=depts,
        output_dir=out,
        dry_run=args.dry_run,
        existing=args.existing,
    )
