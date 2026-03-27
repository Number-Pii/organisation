#!/usr/bin/env python3
"""
init_project.py — Number Pii Project Scaffolder

Creates the standard doc/ folder structure in any project directory.
Run this after the AI coding assistant has determined the project brief and team.

Usage:
    python3 scripts/init_project.py --project-name "My Project"
    python3 scripts/init_project.py --project-name "Client Landing Page" --departments "engineering,design,marketing"
    python3 scripts/init_project.py --project-name "API Build" --departments "engineering" --output-dir /path/to/project

Arguments:
    --project-name   Name of the project (used in file headers)
    --departments    Comma-separated dept names for handover sub-folders (default: engineering)
    --output-dir     Directory to create doc/ in (default: current working directory)
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


def consolidated_handover_template(name):
    return f"""# Consolidated Handover — {name}

> Last updated: {TODAY} | Maintained by: Team Lead / Project Manager

## Purpose
This document is the single source of truth for project state. When starting a new AI session,
instruct the assistant: **"Initialize CLAUDE.md and read doc/handover/consolidated_handover.md"**

---

## Project Summary
<!-- One paragraph: what this project is and who it's for. -->
[FILL IN — copy from project-brief.md]

## Current Status
**Phase:** [Discovery / Design / Development / Testing / Deployment / Maintenance]
**As of:** {TODAY}

## What Has Been Done
<!-- Chronological list of completed work. Update as milestones are hit. -->
- [ ] [Nothing completed yet — project is at kickoff stage]

## What Is In Progress
<!-- What is actively being worked on right now. -->
- [FILL IN]

## What Is Next
<!-- Immediate next steps in priority order. -->
1. [FILL IN]
2. [FILL IN]
3. [FILL IN]

## Blockers & Issues
<!-- Anything blocking progress that needs to be resolved. -->
| Blocker | Owner | Status |
|---------|-------|--------|
| None currently | — | — |

## Key Decisions Made
<!-- Important decisions that affect the project — with rationale. -->
| Decision | Rationale | Date |
|----------|-----------|------|
| [FILL IN] | [FILL IN] | {TODAY} |

## Team Context
<!-- Quick reference: who is doing what. -->
See `doc/team-assignment.md` for full detail.

## Links & Resources
<!-- Figma, repo, staging URL, Notion, etc. -->
| Resource | URL |
|----------|-----|
| Repository | [FILL IN] |
| Staging | [FILL IN] |
| Design | [FILL IN] |

---
*This file is updated by the team lead from department handover notes in `doc/handover/[dept]/`.*
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

def scaffold(project_name: str, departments: list[str], output_dir: Path, dry_run: bool):
    doc_dir = output_dir / "doc"
    handover_dir = doc_dir / "handover"

    files = {
        doc_dir / "project-brief.md":   project_brief_template(project_name),
        doc_dir / "team-assignment.md": team_assignment_template(project_name),
        doc_dir / "workflow.md":         workflow_template(project_name),
        doc_dir / "version_control.md":  version_control_template(project_name),
        handover_dir / "consolidated_handover.md": consolidated_handover_template(project_name),
    }

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
    )
