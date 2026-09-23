# Toolkit Evals

Two kinds of evidence, both run through the same runner adapters
(`scripts/lib/agents.py`), so every eval works with Claude Code (`claude`) and
OpenAI Codex (`codex`) alike.

## Scenario evals: does the toolkit help agents work?

`scripts/run_scenarios.py` gives a real coding agent a natural request inside a
small scaffolded project and scores what it leaves behind. Scoring comes from
the resulting git state, not from a judge model:

| Check | Meaning |
|---|---|
| `tests_pass`, `hidden_tests_pass` | The project's tests pass, plus completion tests the agent never saw |
| `in_scope` | No file changed outside the scenario's allowed paths |
| `no_dash_churn` | No line rewritten only to change its dashes or punctuation |
| `foreign_block_intact` | A block managed by another tool (a Next.js-style `web/AGENTS.md`) is byte-identical |
| `toolkit_untouched` | Nothing inside the vendored `organisation/` folder changed |
| `main_untouched` | No commit on `main`, no push to `main` (the origin rejects it like branch protection) |
| `branch_named` | New branches use `feature/`, `fix/`, `chore/`, or `hotfix/` |
| `handover_written` | The agent left a handover record |
| `validation_run` | The agent ran the project's validation |
| `docs_found` | The agent read the document that holds the answer before editing |
| `parallel_merge_clean` | Two agents working at once produce branches that merge without conflicts |

Metrics also record the context read before the first edit (bytes), shared
handover files edited, cost, turns, and time.

### Layout

- `scenarios/*.toml`: one scenario each (prompt, allowed paths, setup, expectations).
- `scenarios/fixture/`: a small standard-library Python booking service with specs
  and a decision record, scaffolded by the toolkit under test at run time.
- `scenarios/overlays/`: files a scenario's setup commits to a starting branch.
- `scenarios/hidden/`: completion tests copied in only after the agent finishes.
- `scorecards/`: committed summaries of measured runs, one per toolkit version.
- `results/`: raw transcripts and per-run scores (gitignored).

Each run happens in a fresh directory under the system temp folder, never
inside this repo, with a local bare `origin` whose `main` rejects pushes.
Claude runs use `acceptEdits` with a scoped command allowlist; Codex keeps its
workspace-write sandbox with only the scratch directory added.

### Running

```bash
python3 scripts/run_scenarios.py --list
python3 scripts/run_scenarios.py --smoke                        # smoke set, both runners
python3 scripts/run_scenarios.py --all --repeat 3 --runner codex
python3 scripts/run_scenarios.py --scenario bug_fix --toolkit-ref v3.19.1
python3 scripts/run_scenarios.py --setup-only doc_discovery     # build a workspace, run no agent
```

`--toolkit-ref` picks the toolkit under test: `WORKTREE` (the default, including
uncommitted changes) or any tag or commit. Every phase PR includes a smoke-set
table in its description; a measured version gets a scorecard with
`--scorecard evals/scorecards/<version>.json`.

## Skill evals: does a skill improve output?

Each file under `tasks/` defines golden tasks for one domain. The runner executes
every task twice, once bare and once with the skill under test loaded, and
stores both outputs side by side for rubric judging.

```bash
python3 scripts/run_evals.py --list
python3 scripts/run_evals.py --domain backend --runner codex
```

Outputs land in `results/<timestamp>-skills-<runner>/`. Score both outputs per
rubric criterion; keep the skill when it wins, drop or fix it when it doesn't.
A human signs off before a skill is removed or promoted.

### Task file format

```markdown
## Task: short-slug
- **Skill:** @skill-under-test
- **Prompt:** the task given to the model
- **Rubric:**
  - criterion one
  - criterion two
```

Keep 3 to 5 tasks per domain, each small enough to judge in minutes. A task
belongs here when its rubric separates good output from plausible output; a
task any output passes measures nothing.
