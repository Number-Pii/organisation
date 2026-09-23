---
bump: patch
section: Fixed
---
- **The toolkit's `AGENTS.md` no longer points at `STANDARDS.md`.** That file
  was dropped during v4 design: the standards live in the managed block,
  `templates/agents-block.md`. `docs.py check` now also fails when
  `AGENTS.md` or `README.md` names a markdown file, in code formatting, that
  matches no file in the repo. Plain links were already checked; names
  written as code, which is how agent instructions usually refer to files,
  were not.

- **Doc-map summaries describe the document.** `docs.py` summaries, which
  `docs.py map` and `migrate_consumer.py` use for the new `doc/README.md`, now
  prefer the first prose paragraph over numbered lists and `_Generated_`
  lines, and keep only its first sentence. Link syntax is removed, and em and
  en dashes are replaced, so a generated map doesn't bring dashes in. The
  calypad dry run showed the old heuristic picking up a list item and a dash.

### Added
- **`evals/scorecards/v4.0.0.json`:** the full scenario suite on v4.0.0, one
  run per scenario on Claude and Codex. It passed 26 of 26 runs, with no
  edits to shared handover files, no merge conflicts, and no dash churn. This
  is the reference for the next quarterly review.
