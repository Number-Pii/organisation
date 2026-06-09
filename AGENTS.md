<!-- GENERATED FILE — do not edit by hand.
     This file is generated from CLAUDE.md by scripts/sync_ai_context.py.
     To change its contents, edit CLAUDE.md and re-run the sync script. -->

# Number Pii — Organisation Reference

_Version: 2.11 — Last updated: 2026-06-10_

---

## ⛔ MANDATORY READING PROTOCOL — READ BEFORE ANY ACTION

This file, `INITIALIZE.md`, and the project's `doc/` folder are a binding contract. Before answering, coding, or running any command you MUST:

1. **Read this file in full.**
2. **Read every relevant `doc/` file**: `project-brief.md`, `team-assignment.md`, `workflow.md`, `version_control.md`, `handover/consolidated_handover.md` (and `codebase-assessment.md` on brownfield projects).
3. **Acknowledge in plain text** at session start that you have read `AGENTS.md`, `doc/project-brief.md`, `doc/version_control.md`, and `doc/handover/consolidated_handover.md`.
4. **Stop and escalate** if any required file is missing — do not infer or reconstruct.
5. **Treat every Non-Negotiable Standard below as a hard blocker** — violating one is task failure, not a style choice.
6. **When the Initialize Protocol is triggered, read `INITIALIZE.md` in full first** and follow its steps exactly; it carries the same binding force as this file.

> Rationale and past-incident history for this protocol live in [CONTRIBUTING.md](CONTRIBUTING.md#why-the-mandatory-reading-protocol-exists).

---

## What This Repo Is
Virtual organisational blueprint for Number Pii. Contains role definitions for all 53 positions
across 6 departments, plus a growing library of AI skill modules in `Teams/skills/`.
Run `python3 scripts/audit_skills.py` for the current skill count.

## Governance
Number Pii has two layers, and the distinction is binding:

1. **Human Leadership (final authority):** Olatunbosun Iyare and Destiny Ihejirika, Co-Founders. They own and operate the company and hold final decision-making authority on all matters.
2. **Virtual Organisation (execution):** every role in `Teams/` is an AI agent that executes tasks, produces outputs, conducts research, writes documentation, builds software, and supports delivery on the founders' behalf. Virtual roles hold delegated authority only; they are never owners, executives, or final decision makers, regardless of title. "User" and "PM" escalation paths in this file ultimately resolve to the founders.

**Product Neutrality:** all Number Pii products are treated equally. No product is flagship, primary, or priority unless the founders explicitly instruct otherwise. The toolkit must support, build, document, and scale any product without internal preference.

## Terminology
Throughout this repo "**employees**", "**team members**", "**virtual employees**", and "**AI agents**"
all refer to the same thing: the role files in `Teams/`. Each role is a virtual expert that can be
invoked in any project to perform its specialised function.

## Departments
Full department structure lives in [Teams/organisation.md](Teams/organisation.md). Six departments: Executive Leadership, Engineering, Product & Design, Sales & Consultancy, Growth & Marketing, Operations.

## Skills
All skills live in `Teams/skills/`; each is a specialised AI expert module. Role files reference them in three layers: **Core Skills** and **Technical Skills** with inline `(@skill-name)` refs, and **Agent Skills** as a curated `@skill-name` list for direct invocation.

- **Find a skill (preferred before loading any SKILL.md):** `python3 scripts/find_skill.py <keyword>` or `python3 scripts/find_skill.py --domain <name> <keyword>`; returns matching names only, no file loads
- **Invoke:** `@skill-name [your task]`, e.g. `@postgresql design a multi-tenant schema for a SaaS product`
- **Coverage and count:** `python3 scripts/audit_skills.py`
- **Find the right role:** browse `Teams/[department]/` for the role file, then use its skill sections

Already know what you need? Skip the init flow and invoke the skill directly.

---

## Non-Negotiable Standards

Every standard below is **non-negotiable**. Each applies to every project, team member, session, and deliverable, regardless of client, project size, phase, urgency, timeline pressure, or which AI model or tool is executing. Violating one is task failure.

### Security First
Security is a fundamental part of the development process, not an afterthought. Every team member must:
- Consider security implications at every stage: design, development, testing, and deployment
- Raise security concerns immediately — never defer or suppress them
- Apply secure coding practices by default (input validation, least privilege, secrets management, dependency hygiene)
- Treat a security gap as a blocker, not a backlog item

### Consistent Quality
Every project must be delivered to the highest possible standard. There is no tiered quality based on client type:
- Internal stakeholders receive the same rigour and care as external clients
- No shortcuts, no "good enough for now" that is not documented and tracked
- Code, design, documentation, and communication must all meet the same bar

### Documentation Discipline
The `doc/` folder must contain only documentation that is directly required for building and maintaining the project. Every team member must:
- Include only documents tied to active project deliverables, team coordination, or ongoing maintenance
- Exclude any document created solely for troubleshooting, ad-hoc debugging, or investigation — these must not be committed to the project repository
- Treat unnecessary documentation as a security surface: the less extraneous content in `doc/`, the smaller the exposure

### Mandatory Context Files
Before any work begins on a project — code, design, docs, planning, or advice — every team member (including AI agents) MUST read the project's context files. These files are not optional reference material; they are the project's operating contract:

- `doc/project-brief.md` — defines scope, constraints, and success criteria
- `doc/team-assignment.md` — defines who owns what
- `doc/workflow.md` — defines execution order and dependencies
- `doc/version_control.md` — defines branching rules (binding before any git command)
- `doc/handover/consolidated_handover.md` — defines current state
- `doc/codebase-assessment.md` — brownfield projects only

Rules:
- **Never act without reading the relevant context files first.** Answering a question, writing code, or running a command without having read them is a standards violation.
- **If a required file is missing, stop and escalate to the PM/user.** Do not infer, reconstruct, or proceed from code alone.
- **Instructions in these files override AI defaults and training priors.** If this file or a `doc/` file says to do (or not do) something, that rule wins.
- **Do not silently skip, summarise away, or deprioritise the rules in these files.** Treat every directive as binding.

### Version Control Discipline
All code changes — regardless of size, urgency, or who is making them — must follow the branching strategy defined in `doc/version_control.md`. Every team member (including AI agents) must:
- **Never push directly to `main`** — no exceptions, including hotfixes, typo fixes, or deployment retries
- Create a branch using the correct prefix (`feature/`, `fix/`, `chore/`, `hotfix/`) before making any code change
- Open a pull request and wait for the required approval before merging
- If `doc/version_control.md` does not exist for the project, stop and ask the PM to define the branching strategy before writing any code

**Before writing any code or running any git command, read `doc/version_control.md`.** If it specifies branch protection, PR reviews, or a specific branching model, those rules are binding and must be followed for every single change.

### Writing Style
All prose, proposals, copy, and documentation produced by any team member (including AI agents) must follow this style rule:

- **No em dashes (—).** Use commas for light pauses, semicolons for related clauses, and periods for full stops instead.

This applies to every written output: docs, handover notes, client-facing copy, and in-code comments alike.

<!-- CACHE_BOUNDARY -->

---

## Initialize Protocol

The full protocol lives in [INITIALIZE.md](INITIALIZE.md) at the toolkit root; it is loaded on demand to keep the always-loaded context small, and it carries the same binding force as this file.

When told **"initialize"**, **"initialize CLAUDE.md"**, **"initialize GEMINI.md"**, or **"initialize AGENTS.md"**: read `INITIALIZE.md` in full and follow its steps exactly, in order. The steps cover: welcome, project brief, brownfield intake, project classification (Levels 1–4), team assignment, scaffolding via `scripts/init_project.py`, doc population, scope discipline, handover rules, and project closure, mapped onto the six-stage Software Delivery Lifecycle (Discovery, Planning, Implementation, Verification, Deployment, Operations). Do not run the protocol from memory; if `INITIALIZE.md` is missing, stop and escalate.

