# Golden Sample

<!-- Describe the project here in your own words: what it is, how the code is
     laid out, how to run and test it. This part belongs to the project; the
     toolkit never rewrites it. The block between np:begin and np:end is kept
     current by `python3 organisation/scripts/sync_context.py`. -->

**Classification:** Level 4 (Large-Scale Engineering). The quality gates for this level
are in `doc/workflow.md`.

<!-- np:begin -->
## How work is done here

This project runs on the Number Pii toolkit. The toolkit usually sits in a
gitignored `organisation/` folder, but it may be missing, for example in a cloud
session. Everything needed to work safely is in this section; the toolkit adds
depth, not rules.

The founders, Olatunbosun Iyare (he/him) and Destiny Ihejirika (he/him), hold
final authority. AI agents and team roles act on delegated authority.

### Boundaries

These hold for every task. If one looks wrong for your situation, say so
rather than working around it.

- **Never commit or push to `main`.** Work on a branch prefixed `feature/`,
  `fix/`, `chore/`, or `hotfix/`, and merge through a pull request. Review
  happens there.
- **Stay inside the brief.** `doc/project-brief.md` sets the scope. When a
  request goes beyond it, say so and get approval before doing the work; then
  update the brief.
- **Treat security as part of the work.**
  - Validate input.
  - Keep secrets out of code, logs, and commits.
  - Give code only the access it needs.
  - Raise a security concern the moment you see it.
- **Change only what the task needs.**
  - Leave lines you aren't otherwise changing as they are.
  - Never edit generated files, vendored code, lockfiles, or blocks another
    tool manages (`<!-- BEGIN:name -->` to `<!-- END:name -->`). When a tool
    rewrites its own block, commit its version unchanged.
  - Unrelated edits create noisy diffs and merge conflicts.
- **Assume parallel work.**
  - Other agents may be working on other branches right now.
  - Keep your changes and your handover entry on your own branch.
  - Shared state files change only in their own dedicated PRs.
- **Keep `doc/` for documents the project needs.** Debugging notes,
  investigation logs, and scratch files are not committed.

### Where to look

Read what the task needs when it needs it; there is no required reading list.

| When you are | Read |
|---|---|
| Starting or resuming a task | `doc/README.md` (the doc map), then your branch's handover entry if it has one |
| Checking scope or success criteria | `doc/project-brief.md` |
| Branching, committing, releasing | `doc/version_control.md` |
| Picking up work or checking ownership | `doc/workflow.md`, `doc/team-assignment.md`, the task board |
| Changing architecture or a cross-cutting behaviour | `doc/architecture.md` (Level 3 and above), `doc/decisions/` |
| Building to a specification | `doc/specs/` |
| Continuing another agent's work | Their entry in `doc/handover/entries/`, then `doc/handover/STATE.md` |
| Writing docs, reports, or client copy | `organisation/WRITING.md` |
| Needing specialist know-how | `python3 organisation/scripts/find_skill.py <keyword>` |

### Before you open a pull request

1. The project's tests and checks pass (see `doc/workflow.md` for this
   project's quality gates).
2. The diff contains only changes the task needs.
3. Your handover entry is current (format below).
4. Prose you wrote passes `python3 organisation/scripts/check_writing.py <file>`.
5. The PR description says what changed, why, and how it was verified.

### Handover

Each branch keeps one handover file, which only that branch edits:
`doc/handover/entries/YYYY-MM-DD-<branch-name>.md`. Branch slashes become
dashes. `python3 organisation/scripts/handover.py new` creates it; writing it by
hand is fine.

```markdown
---
branch: fix/back-to-back-bookings
issue: 12
agent: claude
---
## Goal
## Done
## Next
## Decisions
## Gotchas
## How to verify
```

Update it before you stop, whether or not the work is finished. It must let
someone else continue without your conversation. To continue another branch's
work on that same branch, edit its entry. On a new branch, create your own
entry and add `continues: <their entry file>` to the front matter.

`doc/handover/STATE.md` is the consolidated project state. It changes only in
`chore/handover-consolidate-*` PRs.
<!-- np:end -->

