---
bump: patch
section: Fixed
---
- **`migrate_consumer.py` covers what the calypad migration needed by hand.**
  - It repoints Markdown links from `consolidated_handover.md` to `STATE.md`.
    Archive folders keep their original links as history.
  - It replaces the v3 "Concurrent Sessions" rules in `version_control.md`
    with the v4 "Parallel Work" rules, but only while that section is still
    the unedited v3 text.
- **`handover.py check` allows the migration branch.** It no longer fails the
  one branch that retires `consolidated_handover.md` and creates `STATE.md`.
  Any later edit to `STATE.md` outside a consolidation branch still fails.
- **`docs.py check` has fewer false alarms.**
  - It reads link paths that contain one level of parentheses, such as
    Next.js route groups like `src/app/(shop)/page.tsx`.
  - It skips links into a missing `organisation/` folder, which is gitignored
    and absent in cloud sessions and worktrees.
  - It skips links inside archive folders.
