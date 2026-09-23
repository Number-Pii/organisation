---
bump: minor
section: Added
---
- **`scripts/migrate_consumer.py` moves a pre-4.0 project to the v4 layout,
  on request.** It is a dry run unless `--apply` is passed, and it never
  commits. It makes these changes:
  - `consolidated_handover.md` becomes `STATE.md`, with its content kept. The
    department notes stay in place, frozen, with `STATE.md` linking to them.
  - It adds the entries folder, and a `doc/README.md` map that lists the
    documents already there.
  - Toolkit-generated context pointers are replaced with `AGENTS.md` and its
    stubs. Any text appended to a pointer is carried over. Hand-written context
    files are recognised by their structure and never touched.
  - It adds the pre-push hook, retires the SessionStart checklist, and updates
    an unmodified protect-main hook.
  - It fixes the placeholder link in `team-assignment.md`, which never
    resolved in any v3 project.

  A second run changes nothing. Status columns in `workflow.md` go only with
  `--strip-status`.
