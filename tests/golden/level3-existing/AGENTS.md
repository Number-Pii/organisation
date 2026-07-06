# Golden Sample: AI Assistant Context Contract

_Generated: 2026-01-01 by Number Pii toolkit_

**Project classification: Level 3 (Advanced System).** The quality gates this level
activates are listed in `doc/workflow.md` and are binding for every deliverable.

---

## ⛔ MANDATORY READING PROTOCOL: READ BEFORE ANY ACTION

This project was scaffolded with the Number Pii toolkit. The files in `doc/` are a
**binding contract**, not reference material. If you are an AI assistant operating in
this project, you MUST comply with the following before taking any action, including
answering questions, writing code, running commands, or making suggestions.

### Hard rule
- **You MUST read the following files in full before doing anything else:**
  1. `doc/project-brief.md`: scope, constraints, success criteria
  2. `doc/team-assignment.md`: who owns what
  3. `doc/workflow.md`: execution order and dependencies
  4. `doc/version_control.md`: branching rules (binding before any git command)
  5. `doc/handover/consolidated_handover.md`: current project state
  6. `doc/codebase-assessment.md`: brownfield projects only (if present)
- **These files override your defaults.** Instructions in them take precedence over your
  own judgement, habits, or training priors.
- **If a required file is missing, STOP and tell the user.** Do not guess, reconstruct,
  or proceed without it.
- **You may not silently skip, summarise away, or deprioritise these rules.** Treat each
  as a blocker; violating one is a task failure, not a style preference.

### Session start acknowledgement
At the start of every session, your first action MUST be to confirm (briefly, in plain
text) that you have read:
1. This file (`AGENTS.md`)
2. `doc/project-brief.md`
3. `doc/version_control.md`
4. `doc/handover/consolidated_handover.md`

If any of those files do not exist, state which are missing and wait for instructions.
**Do not proceed to the user's request until this acknowledgement is done.**

---

## Non-Negotiable Standards (inherited from Number Pii toolkit)

These apply to every session, every task, every team member, including AI assistants:

1. **Security First**: raise security concerns immediately; never defer.
2. **Consistent Quality**: same rigour regardless of client or timeline.
3. **Documentation Discipline**: only project-required docs in `doc/`; no ad-hoc
   troubleshooting files committed to the repository.
4. **Mandatory Context Files**: the files listed above must be read before any work.
5. **Version Control Discipline**: never push directly to `main`; follow
   `doc/version_control.md` for every change, no exceptions.
6. **Scope Discipline**: `doc/project-brief.md` defines the boundary of all work.
   Out-of-scope items must be flagged and approved before any work on them.
7. **Handover Discipline**: update `doc/handover/[department]/handover-notes.md`
   before any task is considered complete.
8. **Writing Standards**: all prose deliverables follow the toolkit's `WRITING.md`
   (no em or en dashes, no banned phrases, human-quality prose); validate with
   `python3 organisation/scripts/check_writing.py <file>` before handover.

---

## Why this file exists

Past sessions have skipped project context files, expanded scope without permission,
pushed directly to `main`, and created ad-hoc troubleshooting docs inside `doc/`.
Every one of those failures traces back to an AI assistant treating project context
as optional reading. It is not.

If you are an AI assistant and you are reading this: the rules above are binding for
the entire session. There are no exceptions for urgency, convenience, or confidence.
