# Toolkit Test Suite

Pytest coverage for the load-bearing scripts. CI runs the whole suite on every
push and PR; run it locally with:

```bash
python3 -m pip install pytest
python3 -m pytest tests/ -q
```

## Layout
| File | Covers |
|------|--------|
| `test_init_project.py` | Scaffold output (golden files per level and `--existing`), overwrite safety, toolkit-root refusal |
| `test_frontmatter.py` | `scripts/lib/frontmatter.py`, including malformed input |
| `test_task_board.py` | `gh_project_sync.py` board and table parsing |
| `test_check_writing.py` | Writing validator rules and exemptions |
| `test_check_version.py` | Version sync checks, including AGENTS.md drift |

## Golden files
`golden/` holds full scaffold trees rendered with a pinned date and project
name. The tests compare `init_project.py` output against them byte for byte,
so any template change fails the suite until the goldens are regenerated:

```bash
python3 tests/generate_goldens.py
git diff tests/golden   # review: the diff IS the template change
```

Never regenerate without reviewing the diff; the review is the point.
