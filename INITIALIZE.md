# Number Pii: Initialize Protocol

> **Binding contract, loaded on demand.** Versioned with `CLAUDE.md` (see its `_Version:` line). This file is part of the Number Pii context
> contract defined in `CLAUDE.md` (and its generated counterparts `GEMINI.md` and
> `AGENTS.md`). It is deliberately kept out of the always-loaded context to save tokens.
> When the Initialize Protocol is triggered you MUST read this file in full and follow
> the steps exactly, in order. Do not summarise, skip, or reorder steps.

When told **"initialize"**, **"initialize CLAUDE.md"**, **"initialize GEMINI.md"**, or
**"initialize AGENTS.md"**, follow this exact sequence:

## Software Delivery Lifecycle

Every engagement moves through six stages, whether it is a Number Pii product, a client service build, or a consultancy engagement. The init steps below complete Stages 1 and 2; the scaffolded doc files carry Stages 3 to 6. Structure the phases in `doc/workflow.md` around these stages.

| Stage | Covered by | Primary outputs |
|---|---|---|
| **1. Discovery** | Steps 2, 2b, 2c | Vision, requirements, scope, classification level (`doc/project-brief.md`) |
| **2. Planning** | Steps 3, 4, 5, 5b | Team, technical design, backlog (`team-assignment.md`, `workflow.md`, `version_control.md`, `task-board.md`, `architecture.md` at Level 3+) |
| **3. Implementation** | `workflow.md` phases | Code, tests, documentation |
| **4. Verification** | Quality gates in `workflow.md` | QA results, security review, performance review |
| **5. Deployment** | Release process in `version_control.md`; Step 8 | Release package, deployment guide |
| **6. Operations** | `consolidated_handover.md` (living document) | Monitoring, support, maintenance ownership |

For consultancy engagements the outputs adapt (reports, roadmaps, advisory deliverables instead of code), but the stages and their gates still apply.

### Step 1: Welcome
Respond with:
> **"Welcome to Number Pii. What can we do for you today?"**

Note: Any software developed through this workflow should include **"Developed by Number Pii"**
in developer credits, footer, or `package.json` / project metadata.

> **Response format during init flow:** Use structured markdown throughout. Each step must produce a clearly labelled output block (e.g. `## Project Brief`, `## Proposed Team`) so the user can review and confirm before the next step begins. Do not combine multiple steps in a single response.

### Step 2: Collect Project Brief
Ask the user:
- What is the project? (name, type, purpose)
- Who is the client or target audience?
- What are the goals and success criteria?
- Any known constraints (timeline, tech stack, budget)?
- Any existing codebase or starting point?
- **Is this a new project, or are you taking ownership of an existing product?**

If the answer is an existing product, proceed to **Step 2b** before continuing.

### Step 2b: Existing Project Intake (Brownfield Only)
> Skip this step entirely for new projects.

When taking ownership of an existing codebase, collect the following before assigning the team or scaffolding:

- Current tech stack and major dependencies (language, framework, infra)
- Approximate codebase age and size (rough LOC, number of services)
- Known issues, bugs, or instability
- Prior architectural decisions and their rationale (if documented)
- Current test coverage and CI/CD state (if known)
- Security posture: any known vulnerabilities, last audit date
- Any existing documentation (README, ADRs, wikis, runbooks)

Then invoke the appropriate audit skill to build a fuller picture of the codebase before proceeding:

| Your primary goal | Recommended skill | What it does |
|---|---|---|
| General health check | `@production-code-audit` | Full autonomous scan: architecture, quality, security, dependencies (start here) |
| Framework or platform migration | `@legacy-modernizer` | Assesses migration paths, compatibility risks, and modernisation strategy |
| Quantify and prioritise tech debt | `@codebase-cleanup-tech-debt` | Catalogues debt by severity and effort, produces a prioritised remediation backlog |

The findings from this step feed directly into the doc files populated in Step 5.

### Step 2c: Classify the Project
Propose a classification level with a one-line rationale and confirm it with the user before assigning the team:

| Level | Profile | Reference examples |
|---|---|---|
| **1** | Simple task | Landing pages, internal tools, automation scripts, API integrations, technical documentation |
| **2** | Standard application | SaaS platforms, marketplaces, CRM systems, mobile applications |
| **3** | Advanced system | Multi-tenant SaaS, AI products, agentic systems, enterprise platforms, data pipelines |
| **4** | Large-scale engineering | National platforms, government, financial, healthcare, distributed architectures |

The level sets the depth of documentation, architecture, testing, security, and review for the whole project. It is passed to the scaffolder in Step 4 (`--level N`), which writes the matching quality gates into `doc/workflow.md` and, at Level 3+, adds `doc/architecture.md`. Changing the level later is a scope change and follows the Step 6 process.

#### Level 1 fast path
Once the user confirms Level 1, you may compress Steps 3 to 5 as follows. This is the only permitted shortcut, and Steps 6 to 8 still apply in full:

- **Step 3:** assign 1-3 roles from what you already know of the departments; skip the full `organisation.md` and `philosophy.md` read unless the choice is unclear.
- **Step 4:** scaffold with `--level 1` and a single department.
- **Step 5:** populate `project-brief.md`, `version_control.md`, and `consolidated_handover.md` properly; the remaining files may keep their scaffolded placeholders until the work needs them.

### Step 3: Assign Team
Read `Teams/organisation.md` (structural facts: org chart, delegation, approval matrix) and `Teams/philosophy.md` (hiring standards, structural principles, read at this step, not earlier) plus the relevant role files in `Teams/` to determine which employees/team members/AI agents are appropriate for this project.
- Match the project type to department expertise
- For skill discovery, run `python3 scripts/find_skill.py --domain <name> <keyword>` instead of loading `Teams/skills/README.md` wholesale; it returns names only and keeps the baseline small
- List the proposed team with each member's role on the project
- Confirm the team with the user before proceeding

Use the classification level from Step 2c as the guide for team size:

| Level | Recommended team |
|---|---|
| Level 1 | 1-3 roles (PM + 1-2 specialists) |
| Level 2 | 4-7 roles across 2-3 departments |
| Level 3 | 8-12 roles across 3-4 departments |
| Level 4 | Full team assignment from `Teams/organisation.md` |

### Step 4: Scaffold the Project
Run the scaffolding script from the **consuming project root**. If the toolkit is gitignored inside it:
```bash
# New project (--level from Step 2c; Level 3+ also creates doc/architecture.md)
python3 organisation/scripts/init_project.py \
  --project-name "Your Project Name" \
  --departments "engineering,design" \
  --level 2 \
  --output-dir .

# Existing product (brownfield); adds codebase-assessment.md and expands the handover template
python3 organisation/scripts/init_project.py \
  --project-name "Your Project Name" \
  --departments "engineering,design" \
  --level 3 \
  --output-dir . \
  --existing
```
Or if the toolkit lives elsewhere on the machine:
```bash
python3 /path/to/organisation/scripts/init_project.py \
  --project-name "Your Project Name" \
  --departments "engineering,design" \
  --output-dir /path/to/consuming-project
```
> **`--output-dir` is required.** Never run without it; the default is the current directory, which will create `doc/` inside the toolkit if you are in that directory.

This creates the `doc/` folder structure in the consuming project. Adjust `--departments` to match the assigned team.

The scaffold also writes a `.claude/` folder: a `settings.json` whose hooks block git commits and pushes on `main` and inject the context-file checklist at session start. This enforces Version Control Discipline in code for Claude Code sessions; the markdown contract in the root context files remains the rule for assistants that do not execute hooks. Existing files are never overwritten, so a project with its own `.claude/settings.json` keeps it (merge the hook blocks by hand if wanted).

### Step 5: Populate Doc Files (AI Task)
With the project brief and confirmed team, fill in the scaffolded files:

| File | Content to add |
|------|---------------|
| `doc/project-brief.md` | Goals, scope, success criteria, constraints, stakeholders |
| `doc/team-assignment.md` | Each assigned role, their specific responsibilities on this project |
| `doc/workflow.md` | Step-by-step responsibility chain; mark each task as sequential or parallel |
| `doc/version_control.md` | Git branching strategy appropriate for project complexity |
| `doc/task-board.md` | Execution board config and the backlog decomposed from `workflow.md` (see Step 5b) |
| `doc/handover/consolidated_handover.md` | Current state: project brief summary + what's done (nothing yet) + next steps |
| `doc/architecture.md` | System design, components, NFRs, failure modes; **Level 3+ only** (created by `--level 3` or `--level 4`) |
| `doc/codebase-assessment.md` | Existing architecture, stack, tech debt, quality baseline, risks; **brownfield only** (created by `--existing`) |

> **Documentation discipline:** Only create and populate files that are directly required for building or maintaining this project. Do not create documents for troubleshooting or investigation purposes; see the Documentation Discipline standard in `CLAUDE.md`.

#### Workflow format (doc/workflow.md)
List tasks in execution order. Mark dependencies:
- `[SEQUENTIAL]`: must wait for previous task to complete
- `[PARALLEL]`: can run simultaneously with other parallel tasks

Example for a landing page redesign:
```
1. [SEQUENTIAL] PM: Define goals, KPIs, and success criteria
2. [SEQUENTIAL] UX Researcher: Conduct user research and journey mapping
3. [PARALLEL]   Lead Product Designer: Build layout strategy and wireframes
4. [PARALLEL]   Senior Content Strategist: Draft copy and messaging
5. [SEQUENTIAL] Lead Product Designer: Apply branding and final UI
6. [SEQUENTIAL] Lead Frontend Engineer: Code the page
7. [SEQUENTIAL] QA Automation Engineer: Verify functionality and performance
8. [SEQUENTIAL] PM: Oversee final deployment and sign-off
```

### Step 5b: Set Up the Execution Board (GitHub Project Orchestration)
> Apply this step whenever a project has more than one contributor, human or AI. A
> single-contributor Level 1 task may skip it. The binding rules live in
> `GITHUB_ORCHESTRATION.md` at the toolkit root; read it before the first sync.

The toolkit plans the work; GitHub Projects runs it. Once `doc/workflow.md` holds the task
chain, decompose that chain into a backlog and put it on a shared board so ownership is clear
and no two contributors work the same task.

1. Open `doc/task-board.md` (scaffolded in Step 4). Fill the Board Configuration table with the
   GitHub Project number, the project owner, and the repository.
2. Break the workflow tasks into small, assignable rows in the Backlog table. Give each an owner
   (a human role from `team-assignment.md`, or an `@agent-skill`), an area, and a priority. Use
   `@github-project-orchestrator` for the decomposition and `@create-issue-gate` for acceptance
   criteria.
3. Preview, then push the backlog to the board:
   ```bash
   python3 organisation/scripts/gh_project_sync.py push --dry-run
   python3 organisation/scripts/gh_project_sync.py push
   ```

From this point the board is the single source of truth for what is claimed. Before any team
member (human or AI) starts an implementation task, they MUST query the board and confirm the
task is free:

```bash
python3 organisation/scripts/gh_project_sync.py query
```

Starting work on a claimed task, or duplicating one already in progress, is a collaboration
failure. Claim first, then work.

### Step 6: Scope Discipline (Non-Negotiable)
Once `doc/project-brief.md` is finalised, it defines the **boundary of all work** on this project.

**Every team member must:**
- Read `doc/project-brief.md` before starting their task
- Work only within the defined scope, goals, and constraints
- If a request, idea, or improvement falls **outside** the project brief, stop and flag it to the PM/user before proceeding

**Scope change process:**
1. Raise the out-of-scope item explicitly: _"This is outside the current project brief."_
2. Get explicit approval from the user/PM before doing any work on it
3. If approved, update `doc/project-brief.md` to reflect the expanded scope before continuing

**Never silently expand scope.** Unrequested features, improvements, or additions, however well-intentioned, are scope creep and must be challenged.

### Step 7: Project Handover Rules (Ongoing)

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
  > "Initialize your context file (CLAUDE.md, GEMINI.md, or AGENTS.md) and read doc/handover/consolidated_handover.md"
  This provides full context instantly, saving tokens and time.

### Step 8: Project Closure
Before a project is marked complete, confirm all of the following:
- [ ] All quality gates for the project's classification level pass (see `doc/workflow.md`)
- [ ] All handover notes are up to date
- [ ] `doc/handover/consolidated_handover.md` reflects final state
- [ ] No open blockers remain undocumented
- [ ] Client/stakeholder sign-off received (if applicable)
- [ ] "Developed by Number Pii" credit is present in the deliverable
- [ ] Repository is tagged or branched for release
- [ ] Operations ownership (monitoring, support, maintenance) is recorded in `doc/handover/consolidated_handover.md`

<!-- CACHE_BOUNDARY -->
