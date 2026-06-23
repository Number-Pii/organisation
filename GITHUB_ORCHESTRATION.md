# Number Pii: GitHub Project Orchestration Layer

> **Binding contract, loaded on demand.** Versioned with `CLAUDE.md` (see its `_Version:` line).
> This file defines how the toolkit turns a project plan into tracked, owned work on a
> GitHub Project board. It carries the same binding force as `CLAUDE.md`. Load it when a
> project uses GitHub Projects for execution tracking, which is the default for any project
> with more than one active contributor (human or AI). The short rules here always apply
> once a board exists, even when this file is not loaded.

## Why this exists

When several contributors share a project, two of them can pick up the same task without
knowing it, dependencies stay implicit, and progress scatters across handover notes. The
toolkit already plans work well: `doc/workflow.md` holds the task chain, `team-assignment.md`
holds who owns what. What it lacked was a live, shared board that every contributor reads
before starting, and writes to as work moves.

This layer closes that gap. The division of labour is simple:

- **The toolkit is the orchestration layer.** It plans, decomposes epics into assignable
  tasks, and delegates ownership.
- **GitHub Projects is the execution layer.** It tracks state, holds the assignee, and is
  the single source of truth for what is claimed and what is free.

Put plainly: the toolkit plans the work, GitHub runs the work.

## Workflow states

Every project board uses the same six states, in this order. Standard states mean a
contributor moving between projects reads the same board everywhere.

| State | Meaning | Lifecycle stage |
|-------|---------|-----------------|
| **Backlog** | Captured, not yet refined or ready to start | Planning |
| **Ready** | Refined, has acceptance criteria, free to claim | Planning |
| **In Progress** | Claimed and being worked | Implementation |
| **Review** | Work done, awaiting review or quality gate | Verification |
| **Blocked** | Cannot progress until a dependency or decision clears | any |
| **Completed** | Merged, verified, and closed | Deployment |

These map onto the six-stage Software Delivery Lifecycle in `INITIALIZE.md`. Planning
produces Backlog and Ready items; Implementation drives In Progress and Review; the
Verification quality gates decide Review to Completed. Blocked is orthogonal: an item in
any active state can become Blocked, and returns to its prior state when the blocker clears.

## Label taxonomy

Labels are how the board stays filterable. Use this standard set; add project-specific
labels only when the standard set cannot express something.

- **Area:** `backend`, `frontend`, `devops`, `security`, `docs`, `design`. One per issue,
  matching the department or skill domain that owns the work.
- **Priority:** `p0` (drop everything), `p1` (this cycle), `p2` (when capacity allows).
  `urgent` is reserved for time-critical incidents and pairs with `p0`.
- **State marker:** `blocked` mirrors the Blocked board state for contributors who filter by
  label rather than column.
- **Owner type:** `human` or `agent`, so the board shows at a glance which work sits with a
  person and which sits with a virtual agent.

## Owner registry

Every issue has exactly one owner. An owner is one of two kinds, and both resolve to roles
the toolkit already defines:

- **Human role:** a position from `Teams/`, such as Lead Backend Engineer or Head of DevOps.
  On the board this is the GitHub user assigned to the issue, carrying the `human` label.
- **Virtual agent or skill:** an AI agent invoked through a skill, such as `@security-audit`,
  `@code-review-excellence`, or `@production-code-audit`. On the board this is recorded in the
  issue body and the `agent` label, since a skill has no GitHub user account.

Owners are drawn from `doc/team-assignment.md` for human roles and from the skill library for
agents. The toolkit adds no separate identity system. To find the right skill for a task, run
`python3 scripts/find_skill.py <keyword>`; to find the right human role, read
`doc/team-assignment.md` and the role files under `Teams/`.

## Ownership locking

A task is **claimed** when it has an assignee and its state is In Progress. On the board, the
assignee and the In Progress state are themselves the lock; no separate ledger file exists to
drift out of sync.

The rule that follows from this:

- A contributor must not start work on a claimed task. Whoever holds the assignment owns it.
- Two paths reopen a claimed task to someone else: reassignment by the project lead, or an
  explicit collaboration request agreed with the current owner. Either way, the change is
  recorded on the board, not assumed.
- Releasing a claim means moving the task back to Ready and clearing the assignee, so the next
  contributor can see it is free.

Because the lock lives on the board, it survives across sessions and across contributors. A
new AI session reads the same claims a human teammate sees.

## Agent awareness rule

Before starting any work, a contributor (human or AI) reads the board. This is not optional:
it is how collisions are prevented.

```bash
# From the consuming project root
python3 organisation/scripts/gh_project_sync.py query
```

The query reports every open item with its owner, state, labels, and blockers. Read it,
confirm the task you intend to start is in Ready and unclaimed, then claim it before writing
any code. An agent that skips this step and duplicates claimed work has violated this contract.

## Independent task injection

Not every task comes from a planning session. A contributor can create an issue directly on
GitHub at any time, for a bug found in passing, a small chore, or a request from a stakeholder.

Manually created issues are first-class members of the board. The toolkit treats them exactly
like generated ones: they take the standard labels, an owner, and a workflow state, and they
appear in the `query` output so every contributor stays aware of them. The only expectation is
that a manual issue carries enough of the standard fields to be claimable, which the board
templates encourage.

## How the pieces fit

Three components carry this layer, each with a single job:

1. **`doc/task-board.md`** (scaffolded into every project by `scripts/init_project.py`) holds
   the board configuration and the initial backlog, decomposed from `doc/workflow.md`. It is
   the structured source the sync script reads.
2. **`scripts/gh_project_sync.py`** is the deterministic bridge to GitHub. It pushes the
   backlog to issues, assigns owners, applies labels, and queries the board for awareness.
   Run any subcommand with `--dry-run` first to see the `gh` calls it would make.
3. **`@github-project-orchestrator`** is the skill that carries the judgement: how to break an
   epic into assignable tasks, match each to an owner, and run the claim-before-work loop. It
   leans on the script for mechanics and on existing skills such as `@github-issue-creator`,
   `@create-issue-gate`, and `@acceptance-orchestrator` for issue quality.

In this version the flow runs one way. A plan in `doc/workflow.md` becomes the backlog in
`doc/task-board.md`, which the script pushes to GitHub, where contributors then track execution.
Reading the board back happens through `query`; the toolkit does not yet write project state into
the doc files automatically.

## Prerequisites

This script needs the GitHub CLI authenticated against the project repository:

```bash
gh auth login          # one-time, interactive
gh auth status         # confirm you are signed in
```

It also needs the target GitHub Project number and owner, recorded in `doc/task-board.md`. If
`gh` is missing, unauthenticated, or the project is not set, the script stops with a clear
message rather than guessing. That follows the toolkit's stop-and-escalate posture: when a
precondition is missing, surface it, do not work around it.

<!-- CACHE_BOUNDARY -->
