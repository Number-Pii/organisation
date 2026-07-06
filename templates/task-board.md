# Task Board: $project_name

> Created: $today | Maintained by: Project Manager / Team Lead
> Execution board configuration for the GitHub Project Orchestration Layer.
> Rules: see `organisation/GITHUB_ORCHESTRATION.md`. Sync: `organisation/scripts/gh_project_sync.py`.

## Purpose
The toolkit plans the work here; GitHub Projects runs it. This file holds the board
configuration and the backlog decomposed from `doc/workflow.md`. The sync script reads the
two tables below, so keep their column names intact.

## Board Configuration
<!-- Fill these in once the GitHub Project exists. The sync script stops with a clear
     message until all three are set. -->

| Setting | Value |
|---------|-------|
| GitHub Project number | TODO |
| Project owner | TODO |
| Repository | TODO |

## Workflow States
Every item moves through these six states (defined in `organisation/GITHUB_ORCHESTRATION.md`):

`Backlog` to `Ready` to `In Progress` to `Review` to `Completed`, with `Blocked` available
from any active state.

## Labels
- **Area:** backend, frontend, devops, security, docs, design (one per issue)
- **Priority:** p0, p1, p2 (urgent pairs with p0 for incidents)
- **Owner type:** human or agent

## Backlog
<!-- Decompose doc/workflow.md tasks into small, assignable rows. Owner is a human role from
     team-assignment.md or an @agent-skill. Owner Type is human or agent. Keep titles unique;
     the sync script skips a title that already exists on the board.

     Example rows (delete the comment markers and edit to use them):
     | 1 | Set up auth database schema | backend | p1 | Lead Backend Engineer | human | Ready | none |
     | 2 | Implement JWT middleware    | backend | p1 | @backend-dev-guidelines | agent | Backlog | 1 |
-->

| ID | Title | Area | Priority | Owner | Owner Type | State | Depends On |
|----|-------|------|----------|-------|------------|-------|------------|

## Claiming Work (read before starting)
Before starting any task, run `python3 organisation/scripts/gh_project_sync.py query` to see
who owns what. A task is claimed once it has an assignee and sits in In Progress; do not start
a claimed task. Reassignment or an agreed collaboration request is the only exception, and the
change is recorded on the board.
