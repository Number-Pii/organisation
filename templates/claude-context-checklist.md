# $project_name: session start checklist (injected by SessionStart hook)

Before acting on any request in this project, complete the Mandatory Reading
Protocol from the root context file. Read these in full, in order:

| # | File | What it defines |
|---|------|-----------------|
| 1 | `doc/project-brief.md` | Scope, constraints, success criteria |
| 2 | `doc/team-assignment.md` | Ownership |
| 3 | `doc/workflow.md` | Execution order and quality gates |
| 4 | `doc/version_control.md` | Branching rules (binding before any git command) |
| 5 | `doc/handover/consolidated_handover.md` | Current project state |
| 6 | `doc/codebase-assessment.md` (if present) | Brownfield context |

Then acknowledge in plain text that you have read files 1, 4, and 5 plus the
root context file. If any required file is missing, stop and tell the user.

Git guardrail: a PreToolUse hook blocks commits and pushes on `main`; work on
a `feature/`, `fix/`, `chore/`, or `hotfix/` branch and open a PR.
