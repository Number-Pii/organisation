---
bump: major
section: Breaking
---
- **`AGENTS.md` is the one instruction file.** `CLAUDE.md` and `GEMINI.md` are
  now stubs that import it with `@AGENTS.md`, in the toolkit and in every new
  scaffold. `sync_ai_context.py` and its CI step are gone, along with 22 KB of
  near-duplicate text.
- **Context is progressive.** The fixed reading list, the session-start
  acknowledgement, the "task failure" and "override your training" language,
  and the SessionStart checklist hook are removed. Each project's `AGENTS.md`
  instead carries a managed block of about 90 lines covering:
  - boundaries, each with its reason
  - a routing table ("when you are X, read Y")
  - the PR checklist
  - the handover format

  The block is self-contained, so cloud agents that clone a project without
  `organisation/` still have every rule they need.
- **Handover is per branch.** Each branch writes only
  `doc/handover/entries/<date>-<branch>.md`. `doc/handover/STATE.md` replaces
  `consolidated_handover.md` and changes only in
  `chore/handover-consolidate-*` PRs. The per-department `handover-notes.md`
  files are no longer scaffolded. The v3.19.1 baseline showed the shared
  notes file conflicting in 2 of 3 parallel-agent pairs.

### Added
- `scripts/handover.py` (`new`, `status`, `check`, `consolidate`) replaces
  `draft_handover.py` and `check_handover.py`.
- `scripts/docs.py` (`map`, `check`): `doc/README.md` is the doc map. Files
  inside mapped folders (`decisions/`, `specs/`, `runbooks/`, `reference/`)
  need no index edit. `check` fails on unmapped top-level files, unknown
  folders, and broken relative links, and CI runs it on the toolkit itself.
- `scripts/sync_context.py` refreshes the managed block
  (`<!-- np:begin -->` to `<!-- np:end -->`) in a project's `AGENTS.md`. It
  writes only on change and has no version or date to churn. It refuses files
  without the block unless `--append` is passed.
- A git-native `.githooks/pre-push` in every scaffold refuses pushes to
  `main`, whichever agent or person runs git.

### Changed
- **The Claude Code protect-main hook respects worktrees.** It checks the
  repository each git command targets (`git -C`, `cd <dir> &&`). It no
  longer blocks agents committing in a linked worktree on their own branch,
  which the v3.19.1 baseline caught happening. It also no longer blocks
  branches such as `feature/main-menu`. `--no-claude-hooks` skips the hook.
- **`INITIALIZE.md` describes outcomes, not a script.** It covers the
  decisions the user makes and what an initialized project contains.
- **The board owns live status.** `gh_project_sync.py sync` only reports
  differences unless `--write-back` is passed. `query` shows board status and
  blocking issues. `doc/workflow.md` no longer has Status columns.
- **Subagent governance notes follow the new boundaries.** The note
  `build_agents.py` writes points to the project's `AGENTS.md`.

### Removed
- `CACHE_BOUNDARY` sentinels (nothing parsed them), the separate protocol
  `_Version` line, and README's "Document Version".

### Migration
- Nothing changes in existing consumer projects until someone acts. Their
  `doc/` and context files stay as they are. `scripts/migrate_consumer.py`
  (next PR) moves a project to the v4 layout on request, with a dry run
  first.
