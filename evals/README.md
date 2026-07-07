# Toolkit Skill Evals

Measures whether a curated skill actually improves output, turning skill
curation from taste into evidence. Each task file under `tasks/` defines
golden tasks for one domain; the runner executes every task twice, once bare
and once with the skill under test loaded, and stores both outputs side by
side for rubric judging.

## Running

```bash
# List tasks without running anything
python3 scripts/run_evals.py --list

# Run one domain (needs the `claude` CLI on PATH)
python3 scripts/run_evals.py --domain backend

# Run everything
python3 scripts/run_evals.py
```

Outputs land in `evals/results/<timestamp>/` (gitignored) as one markdown file
per task holding the bare run, the skill run, and the task's rubric. Judging
is by rubric: score both outputs per criterion, keep the skill when it wins,
demote or fix it when it loses. An LLM can apply the rubric, but a human signs
off before a tier changes.

## Task file format

Each `tasks/<domain>.md` holds one or more tasks:

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
