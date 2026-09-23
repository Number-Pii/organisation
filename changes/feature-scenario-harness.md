---
bump: minor
section: Added
---
- **Scenario evals.** `scripts/run_scenarios.py` runs real coding agents (Claude
  Code and OpenAI Codex) through twelve scenarios in a scaffolded fixture
  project: an issue to a feature, an unfamiliar area, a bug fix, a new
  component, an architecture change, validation, PR preparation, a handover,
  two agents in parallel, continuing another agent's branch, and doc discovery.
  Scoring comes from the git state the agent leaves: hidden completion tests,
  scope, dash churn, main-branch safety, handover, doc discovery, and merge
  conflicts between parallel agents. No judge model.
- **Runner adapters.** `scripts/lib/agents.py` gives every eval one interface to
  either CLI, so `run_evals.py` gains `--runner codex` and no script hard-codes
  one vendor.
- **Baseline scorecard.** `evals/scorecards/v3.19.1-baseline.json` records how
  v3.19.1 performs, the reference every v4 phase is measured against.
