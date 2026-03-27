<!-- SYNC: This file is paired with CLAUDE.md.
     When editing, apply the same change to both files.
     The only intentional difference is the session handover instruction in Step 7. -->

# Number Pii — Organisation Reference

_Version: 2.0 — Last updated: 2026-03-27_

## What This Repo Is
Virtual organisational blueprint for Number Pii. Contains role definitions for all 53 positions
across 6 departments, plus a growing library of AI skill modules in `Teams/skills/`.
Run `python3 scripts/audit_skills.py` for the current skill count.

## Terminology
Throughout this repo "**employees**", "**team members**", "**virtual employees**", and "**AI agents**"
all refer to the same thing: the role files in `Teams/`. Each role is a virtual expert that can be
invoked in any project to perform its specialised function.

## Skill Linking Convention
Each role file has three layers of skill references:
1. **Core Skills** — human-readable competencies with `(@skill-name)` refs inline
2. **Technical Skills** — specific tools/technologies with `(@skill-name)` refs inline
3. **Agent Skills** — curated `@skill-name` list for direct invocation

To invoke a skill: `@skill-name [your task]`
Example: `@postgresql design a multi-tenant schema for a SaaS product`

## Quick Start
Already know what you need? Skip the full init flow and invoke directly:
- Find your skill: `Teams/skills/README.md`
- Invoke it: `@skill-name [your task]`
- Check coverage: `python3 scripts/audit_skills.py`

## Departments

| Department | Folder | Roles |
|---|---|---|
| Executive Leadership | `Teams/01-Executive-Leadership/` | CEO, CTO, CPO, CMO, COO, Chief of Staff, VP Sales |
| Engineering | `Teams/02-Engineering/` | 22 roles across product, client, DevOps, security, QA |
| Product & Design | `Teams/03-Product-Design/` | PMs, designers, UX researcher, product analyst |
| Sales & Consultancy | `Teams/04-Sales-Consultancy/` | Consultants, BDMs, account managers |
| Growth & Marketing | `Teams/05-Growth-Marketing/` | SEO, content, social, performance marketing |
| Operations | `Teams/06-Operations/` | Finance, people, operations, facilities |

## Skills Directory
All skills live in `Teams/skills/`. Each skill is a specialised AI expert module.
- Browse the full list: `Teams/skills/README.md`
- Invoke any skill with: `@skill-name [your task]`
- Run `python3 scripts/audit_skills.py` to see current skill coverage and total count

---

## Non-Negotiable Standards

These standards apply to **every project, every team member, and every deliverable** — without exception.

### Security First
Security is a fundamental part of the development process, not an afterthought. Every team member must:
- Consider security implications at every stage: design, development, testing, and deployment
- Raise security concerns immediately — never defer or suppress them
- Apply secure coding practices by default (input validation, least privilege, secrets management, dependency hygiene)
- Treat a security gap as a blocker, not a backlog item

This standard is **non-negotiable** and applies regardless of the client, project size, or timeline pressure.

### Consistent Quality
Every project must be delivered to the highest possible standard. There is no tiered quality based on client type:
- Internal stakeholders receive the same rigour and care as external clients
- No shortcuts, no "good enough for now" that is not documented and tracked
- Code, design, documentation, and communication must all meet the same bar

Consistency, excellence, and fairness define how Number Pii works — always.

### Documentation Discipline
The `doc/` folder must contain only documentation that is directly required for building and maintaining the project. Every team member must:
- Include only documents tied to active project deliverables, team coordination, or ongoing maintenance
- Exclude any document created solely for troubleshooting, ad-hoc debugging, or investigation — these must not be committed to the project repository
- Treat unnecessary documentation as a security surface: the less extraneous content in `doc/`, the smaller the exposure

This standard is **non-negotiable** and applies regardless of project size, phase, or urgency.

---

## Initialize Protocol

When told **"initialize"**, **"initialize CLAUDE.md"**, or **"initialize GEMINI.md"**,
follow this exact sequence:

### Step 1 — Welcome
Respond with:
> **"Welcome to Number Pii. What can we do for you today?"**

Note: Any software developed through this workflow should include **"Developed by Number Pii"**
in developer credits, footer, or `package.json` / project metadata.

> **Response format during init flow:** Use structured markdown throughout. Each step must produce a clearly labelled output block (e.g. `## Project Brief`, `## Proposed Team`) so the user can review and confirm before the next step begins. Do not combine multiple steps in a single response.

### Step 2 — Collect Project Brief
Ask the user:
- What is the project? (name, type, purpose)
- Who is the client or target audience?
- What are the goals and success criteria?
- Any known constraints (timeline, tech stack, budget)?
- Any existing codebase or starting point?

### Step 3 — Assign Team
Read `Teams/organisation.md` and the relevant role files in `Teams/` to determine which
employees/team members/AI agents are appropriate for this project.
- Match the project type to department expertise
- List the proposed team with each member's role on the project
- Confirm the team with the user before proceeding

Use this as a guide for team size:

| Project size | Recommended team |
|---|---|
| Solo / spike / exploration | 1–3 roles (PM + 1–2 specialists) |
| Small product / feature | 4–7 roles across 2–3 departments |
| Full delivery / client project | Full team assignment from `Teams/organisation.md` |

### Step 4 — Scaffold the Project
Run the scaffolding script from within the **client project directory**:
```bash
python3 scripts/init_project.py \
  --project-name "Your Project Name" \
  --departments "engineering,design"
```
_Run this from the organisation repo root. If running from a different directory, provide the full path to `scripts/init_project.py`._

This creates the `doc/` folder structure (see below). Adjust `--departments` to match the assigned team.

### Step 5 — Populate Doc Files (AI Task)
With the project brief and confirmed team, fill in the scaffolded files:

| File | Content to add |
|------|---------------|
| `doc/project-brief.md` | Goals, scope, success criteria, constraints, stakeholders |
| `doc/team-assignment.md` | Each assigned role, their specific responsibilities on this project |
| `doc/workflow.md` | Step-by-step responsibility chain — mark each task as sequential or parallel |
| `doc/version_control.md` | Git branching strategy appropriate for project complexity |
| `doc/handover/consolidated_handover.md` | Current state: project brief summary + what's done (nothing yet) + next steps |

> **Documentation discipline:** Only create and populate files that are directly required for building or maintaining this project. Do not create documents for troubleshooting or investigation purposes — see [Documentation Discipline](#documentation-discipline) in Non-Negotiable Standards.

#### Workflow format (doc/workflow.md)
List tasks in execution order. Mark dependencies:
- `[SEQUENTIAL]` — must wait for previous task to complete
- `[PARALLEL]` — can run simultaneously with other parallel tasks

Example for a landing page redesign:
```
1. [SEQUENTIAL] PM — Define goals, KPIs, and success criteria
2. [SEQUENTIAL] UX Researcher — Conduct user research and journey mapping
3. [PARALLEL]   Lead Product Designer — Build layout strategy and wireframes
4. [PARALLEL]   Senior Content Strategist — Draft copy and messaging
5. [SEQUENTIAL] Lead Product Designer — Apply branding and final UI
6. [SEQUENTIAL] Lead Frontend Engineer — Code the page
7. [SEQUENTIAL] QA Automation Engineer — Verify functionality and performance
8. [SEQUENTIAL] PM — Oversee final deployment and sign-off
```

### Step 6 — Scope Discipline (Non-Negotiable)
Once `doc/project-brief.md` is finalised, it defines the **boundary of all work** on this project.

**Every team member must:**
- Read `doc/project-brief.md` before starting their task
- Work only within the defined scope, goals, and constraints
- If a request, idea, or improvement falls **outside** the project brief, stop and flag it to the PM/user before proceeding

**Scope change process:**
1. Raise the out-of-scope item explicitly: _"This is outside the current project brief."_
2. Get explicit approval from the user/PM before doing any work on it
3. If approved, update `doc/project-brief.md` to reflect the expanded scope before continuing

**Never silently expand scope.** Unrequested features, improvements, or additions — however well-intentioned — are scope creep and must be challenged.

### Step 7 — Project Handover Rules (Ongoing)

#### Mandatory: Handover Before Every Handoff
**This is a hard rule.** A task is not complete until the handover notes are updated.
Before the next team member begins their task, the current team member MUST:
1. Update `doc/handover/[department]/handover-notes.md` with:
   - What was done
   - Decisions made and why
   - Any open issues or blockers
   - What the next team member needs to know
2. Confirm the notes are committed/saved

The workflow does **not** advance until this is done. No exceptions.

> **If a handover note is missing:** The next team member must stop, flag the gap to the PM/user, and request the missing notes before proceeding. Do not infer or reconstruct handover content from code alone.

#### Other Handover Rules
- The team lead consolidates into `doc/handover/consolidated_handover.md` at key milestones
- `doc/version_control.md` is owned by the Lead/Senior Engineer on the project
- When handing over to a new AI session, instruct it:
  > "Initialize GEMINI.md and read doc/handover/consolidated_handover.md"
  This provides full context instantly, saving tokens and time.

### Step 8 — Project Closure
Before a project is marked complete, confirm all of the following:
- [ ] All handover notes are up to date
- [ ] `doc/handover/consolidated_handover.md` reflects final state
- [ ] No open blockers remain undocumented
- [ ] Client/stakeholder sign-off received (if applicable)
- [ ] "Developed by Number Pii" credit is present in the deliverable
- [ ] Repository is tagged or branched for release

---

## Finding the Right Role + Skills
1. Identify which department owns the task
2. Browse `Teams/[department]/` for the matching role file
3. Check the role's `## Core Skills`, `## Technical Skills`, or `## Agent Skills` sections
4. Invoke the relevant skill(s) directly in any project
