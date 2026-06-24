---
name: github-project-orchestrator
description: Use when a project has more than one contributor and work must be tracked on a shared GitHub Project board, so tasks have clear owners and no two contributors duplicate effort.
risk: safe
source: internal
date_added: "2026-06-23"
domain: "Planning & Workflow"
size_class: s
summary: Turn a project plan into owned, tracked issues on a GitHub Project board, then claim work safely without collisions.
detail_sections:
  - When to Use This Skill
  - The Orchestration Loop
  - Decomposing Epics into Tasks
  - Matching Owners
  - Workflow States and Locking
  - Running the Sync
  - Related Skills
---

# GitHub Project Orchestrator

The toolkit plans the work; GitHub Projects runs the work. This skill carries the judgement
for the handoff: how to break a plan into assignable tasks, give each an owner, and run the
claim-before-work loop that keeps several contributors from colliding. The binding rules live
in `GITHUB_ORCHESTRATION.md` at the toolkit root; read it once before your first sync on a
project, then use this skill for the day-to-day flow.

## When to Use This Skill

Reach for it in two moments:

- **At the Planning stage**, once `doc/workflow.md` holds the task chain, to decompose that
  chain into a backlog and push it to a GitHub Project board.
- **Before starting any implementation task**, to query the board, confirm the task is free,
  and claim it. An agent or person who skips this step risks duplicating claimed work.

If a project has a single contributor and no shared board, you do not need this skill. The
board earns its keep once two or more contributors share the project.

## The Orchestration Loop

The loop has four moves, and they repeat as the project runs:

1. **Decompose.** Convert epics and `doc/workflow.md` tasks into small, assignable issues with
   testable acceptance criteria. Record them in `doc/task-board.md`.
2. **Push.** Send the backlog to GitHub with `gh_project_sync.py push`. Each row becomes an
   issue with its area and priority labels, an owner, and a starting workflow state.
3. **Claim.** Before working a task, run `query`, pick a task in Ready that no one owns, and
   assign yourself. Move it to In Progress.
4. **Advance.** As work moves, update state through Review to Completed, and surface blockers
   as they appear.

## Decomposing Epics into Tasks

A good task is small enough for one owner to finish and specific enough to verify. Split by
deliverable, not by activity. Take an epic such as "Build authentication system" and break it
into independent units:

- Set up the auth database schema
- Implement JWT middleware
- Create the login API endpoint
- Create the password reset workflow
- Add OAuth integration

Each becomes one issue. For the acceptance-criteria gate that decides whether a task is Ready
or stays in Backlog, lean on `@create-issue-gate`; for turning rough notes into clean issue
text, `@github-issue-creator` does the shaping.

## Matching Owners

Every task gets exactly one owner, and an owner is one of two kinds:

- A **human role** from `doc/team-assignment.md`, such as Lead Backend Engineer. On the board
  this is a GitHub assignee carrying the `human` label.
- A **virtual agent or skill**, such as `@security-audit` or `@code-review-excellence`. A skill
  has no GitHub account, so it is recorded in the issue body and the `agent` label.

To find the right human role, read `doc/team-assignment.md` and the role files under `Teams/`.
To find the right agent skill for a task, run `python3 scripts/find_skill.py <keyword>` rather
than loading skill files blindly.

## Workflow States and Locking

Every board uses the same six states: Backlog, Ready, In Progress, Review, Blocked, Completed.
A task is claimed once it has an assignee and sits in In Progress, and that pairing is the lock
itself. No separate ledger exists, so the board never drifts.

Respect the lock. Do not start a claimed task. Reassignment by the project lead or an agreed
collaboration request are the only ways a claimed task moves to someone else, and either change
is recorded on the board rather than assumed. To release a task, move it back to Ready and clear
the assignee so the next contributor sees it is free.

## Running the Sync

The deterministic mechanics live in `scripts/gh_project_sync.py`. Preview any command with
`--dry-run` before applying it; the flag works before or after the subcommand:

```bash
# See current ownership before claiming anything
python3 organisation/scripts/gh_project_sync.py query

# Preview, then push the backlog to the board
python3 organisation/scripts/gh_project_sync.py push --dry-run
python3 organisation/scripts/gh_project_sync.py push

# Claim a task: assign yourself and move it to In Progress
python3 organisation/scripts/gh_project_sync.py assign --issue 42 \
  --assignee your-handle --state "In Progress"
```

The script needs `gh` authenticated (`gh auth login`) and a filled Board Configuration table in
`doc/task-board.md`. When a precondition is missing, it stops with a clear message instead of
guessing.

## Related Skills

- `@create-issue-gate`: gate a task on testable acceptance criteria before it reaches Ready.
- `@github-issue-creator`: turn messy notes, logs, or screenshots into clean issue text.
- `@github-workflow-automation`: deeper GitHub API and automation patterns beyond this sync.
- `@acceptance-orchestrator`: drive a single issue from intake through review to acceptance.
