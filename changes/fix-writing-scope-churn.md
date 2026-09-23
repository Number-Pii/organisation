---
bump: patch
section: Fixed
---
- **The writing standard no longer causes git churn.** The dash ban and the
  rest of `WRITING.md` now cover only prose the agent writes. Lines it isn't
  otherwise changing, generated and vendored files, lockfiles, code comments,
  and blocks managed by other tools are out of scope. The main case is the
  `<!-- BEGIN:nextjs-agent-rules -->` block that Next.js rewrites into
  `AGENTS.md` and `CLAUDE.md` on every `next dev`. Agents had been
  "fixing" its em dashes, and Next kept putting them back. The same scope
  clause is in `CLAUDE.md`, `WRITING.md`, and the scaffolded context files.
- **`check_writing.py` respects that scope.** It skips `BEGIN:name`/`END:name`
  and `np:begin`/`np:end` blocks (but not markers quoted in inline code) and
  files under `node_modules`, `vendor`, `dist`, `build`, `.next`, and
  lockfiles. It also gains `--profile technical|internal|marketing`.
- **Generators write only when content changes.** `build_agents.py`,
  `build_org.py`, `build_skills_index.py`, and `sync_ai_context.py` share
  `scripts/lib/files.py:write_if_changed`, and tests check that a second run
  leaves every output untouched.
- **Scaffolded context files carry no render date.** The `_Generated: <date>`
  line is gone from `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`, so
  re-rendering them on another day produces identical bytes.
- **No em dashes in generated headers.** They came from the header strings in
  `sync_ai_context.py`. An agent that "fixed" them broke the sync check.

### Changed
- `harness`, `robust`, and `leverage` move from the banned list to "use
  sparingly". All three are ordinary engineering terms.

### Migration
- Existing consumer context files keep their `_Generated` line until they are
  next refreshed. Nothing needs rewriting.
