# Handover Archive: $project_name

> Purpose: keep `consolidated_handover.md` lean (≤150 lines, ~4K tokens) regardless of project age.

## Why this exists
Without rolling, `consolidated_handover.md` grows unbounded; by month three of a real project,
it commonly exceeds 1,000 lines and becomes the single largest file loaded every session.
Rolling prior phases into dated archive files keeps session startup cost constant.

## When to roll
At every milestone, or at month-boundaries, whichever comes first. The team lead:

1. Creates `archive/{YYYY-MM}.md` (e.g. `2026-04.md`) for the just-completed phase
2. Moves the completed items from `consolidated_handover.md`'s "What Has Been Done" and
   any superseded decisions from "Key Decisions"
3. Leaves in `consolidated_handover.md` **only** work from the current/next phase
4. Adds a one-line entry to the Archive Index below

## Archive Index
| File | Covers | Phase |
|------|--------|-------|
| *(none yet)* | none | none |

## What to include in an archive file
- Timeline of completed work (dated bullets)
- Decisions made during the archived window, with rationale
- Links to PRs / commits / artefacts from that phase
- Anything future sessions may want to consult for *why*, not *what*

## What NOT to archive
- In-progress work, active blockers, live stakeholders; those belong in `consolidated_handover.md`
- Anything the current phase still depends on
