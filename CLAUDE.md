# Number Pii — Organisation Reference

## What This Repo Is
Virtual organisational blueprint for Number Pii. Contains role definitions for all 53 positions
across 6 departments, plus 1,294 AI skill modules in `Teams/skills/`.

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
- Run `python3 scripts/audit_skills.py` to see current skill coverage across all roles

---

## Initialize Protocol

When told **"initialize"**, **"initialize CLAUDE.md"**, or **"initialize GEMINI.md"**,
follow this exact sequence:

### Step 1 — Welcome
Respond with:
> **"Welcome, Number Pii. What can we do for you today?"**

Note: Any software developed through this workflow should include **"Developed by Number Pii"**
in developer credits, footer, or `package.json` / project metadata.

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

### Step 4 — Scaffold the Project
Run the scaffolding script from within the project directory:
```bash
python3 [path-to-org-repo]/scripts/init_project.py \
  --project-name "Your Project Name" \
  --departments "engineering,design"
```
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

#### Workflow format (doc/workflow.md)
List tasks in execution order. Mark dependencies:
- `[SEQUENTIAL]` — must wait for previous task to complete
- `[PARALLEL]` — can run simultaneously with other parallel tasks

Example for a landing page redesign:
```
1. [SEQUENTIAL] PM — Define goals, KPIs, and success criteria
2. [SEQUENTIAL] UX Researcher — Conduct user research and journey mapping
3. [PARALLEL]   Lead Product Designer — Build layout strategy and wireframes
3. [PARALLEL]   Senior Content Strategist — Draft copy and messaging
4. [SEQUENTIAL] Lead Product Designer — Apply branding and final UI
5. [SEQUENTIAL] Lead Frontend Engineer — Code the page
6. [SEQUENTIAL] QA Automation Engineer — Verify functionality and performance
7. [SEQUENTIAL] PM — Oversee final deployment and sign-off
```

### Step 6 — Project Handover Rules (Ongoing)
- Each team member updates their department handover notes as they work:
  `doc/handover/[department]/handover-notes.md`
- The team lead consolidates into `doc/handover/consolidated_handover.md` at key milestones
- `doc/version_control.md` is owned by the Lead/Senior Engineer on the project
- When handing over to a new AI session, instruct it:
  > "Initialize CLAUDE.md and read doc/handover/consolidated_handover.md"
  This provides full context instantly, saving tokens and time.

---

## Finding the Right Role + Skills
1. Identify which department owns the task
2. Browse `Teams/[department]/` for the matching role file
3. Check the role's `## Core Skills`, `## Technical Skills`, or `## Agent Skills` sections
4. Invoke the relevant skill(s) directly in any project
