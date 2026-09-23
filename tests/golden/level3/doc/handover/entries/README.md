# Handover entries

One file per branch, named `YYYY-MM-DD-<branch-name>.md` with slashes turned
into dashes (`2026-09-23-fix-back-to-back-bookings.md`). Only that branch edits
its file, so parallel pull requests never conflict here.

Create one with `python3 organisation/scripts/handover.py new`, or copy the
headings from any existing entry. Update it before you stop, finished or not,
so the next person can continue without your conversation. To continue someone
else's work on a new branch, start your own entry and add `continues:` with
their file name to the front matter.

Entries stay here after their branch merges; `../STATE.md` records up to which
date they have been consolidated.
