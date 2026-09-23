# $project_name documentation

This is the map of `doc/`. Read what your task needs; nobody reads all of it.

| Path | What it holds | Read it when |
|---|---|---|
| `project-brief.md` | Scope, goals, constraints, success criteria | Checking whether a request is in scope |
| `team-assignment.md` | Roles and what each owns | Deciding who approves or owns something |
| `workflow.md` | Planned tasks, their order, and this level's quality gates | Picking up work or preparing a release |
| `version_control.md` | Branching, review, and release rules | Before branching, committing, or releasing |
| `task-board.md` | Backlog and GitHub Project configuration | Claiming or planning tasks |
| `architecture.md` | System design, components, and failure modes (Level 3 and above) | Changing structure, interfaces, or non-functional behaviour |
| `codebase-assessment.md` | Stack, debt, and risks found when the product was taken over (brownfield only) | Working on inherited code |
| `handover/STATE.md` | Consolidated project state | Getting oriented |
| `handover/entries/` | One handover file per branch | Starting, resuming, or continuing a branch |
| `decisions/` | One dated file per durable decision | Changing anything a decision covers |
| `specs/` | Feature and interface specifications | Building to a spec |
| `runbooks/` | Operational procedures | Operating or supporting the system |
| `reference/` | Other long-lived reference material | When a spec or decision points to it |

Files inside these folders are found by listing the folder, so adding one
needs no change here. A new top-level file in `doc/` does need a row, and
`python3 organisation/scripts/docs.py check` fails until it has one.
`python3 organisation/scripts/docs.py map` prints every document with its
summary.

Create a folder when its first document arrives. Debugging notes and
investigation logs do not belong in `doc/`.
