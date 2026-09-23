# Number Pii Organisation Toolkit

> **Reached this file from inside another project?** This folder is a vendored,
> read-only copy of the toolkit. Your project's own root `AGENTS.md` (or
> `CLAUDE.md`) is the file that governs your work. Don't edit anything here;
> read what your project's routing table points you to and return.

This repository is Number Pii's toolkit for AI-assisted delivery. Consuming
projects clone it into a gitignored `organisation/` folder and use it for the
following:
- a project scaffold (`scripts/init_project.py`)
- the standards every project inherits (`STANDARDS.md`)
- the virtual organisation of 53 roles (`Teams/`)
- a library of skills (`Teams/skills/`)
- supporting scripts

This file is for agents and people maintaining the toolkit itself. The toolkit
has no `doc/` folder of its own: it is not a delivery project.

Throughout the toolkit, "employees", "team members", and "AI agents" mean the
same thing: the role files in `Teams/`.

## Governance

The founders hold final authority on every matter: Olatunbosun Iyare (he/him)
and Destiny Ihejirika (he/him). Every role under `Teams/` is an AI agent with
delegated authority only, whatever its title. All Number Pii products are
treated equally; none is flagship unless the founders say so.

## Boundaries

- **Never commit or push to `main`.** Branch with `feature/`, `fix/`, `chore/`
  or `hotfix/`, open a PR, and let a founder merge it. Branch protection
  enforces this.
- **Add a changelog fragment, not a version bump.** Every PR adds
  `changes/<branch-name>.md` ([changes/README.md](changes/README.md)).
  Releases happen in their own PR through `scripts/release.py`.
- **Generated files are regenerated, never hand-edited.** When the source
  changes, run the matching script:

  | Generated file(s) | Regenerate with |
  |---|---|
  | `Teams/skills/skills-index.json`, `Teams/skills/CATEGORIES.md` | `build_skills_index.py` |
  | `Teams/org.json` | `build_org.py` |
  | `agents/np-*.md` | `build_agents.py` |
  | `tests/golden/` | `tests/generate_goldens.py` |

  If a generated file conflicts in a rebase, regenerate it; don't merge it by hand.
- **Scaffold wording lives in `templates/`.** Don't put it inline in Python.
  Template changes regenerate the goldens, and the golden diff is part of the
  review.
- **Consumers are not touched from here.** Nothing in this repo writes into a
  consuming project except `init_project.py` (which never overwrites) and the
  opt-in scripts the founders run on request.
- **Change only what the task needs.** The writing standard covers prose you
  write, not lines you are passing by.

## Where to look

| Task | Start with |
|---|---|
| Change what consuming projects are told | `templates/agents-block.md` (the managed block), `STANDARDS.md` |
| Change the scaffold | `templates/`, `scripts/init_project.py`, `tests/test_init_project.py` |
| Change the Initialize Protocol | `INITIALIZE.md` |
| Change handover or doc conventions | `templates/`, `scripts/handover.py`, `scripts/docs.py` |
| Add, remove, or review a skill | [CONTRIBUTING.md](CONTRIBUTING.md#adding-a-new-skill), `scripts/audit_skills.py` |
| Change a role | `Teams/<department>/`, then regenerate `org.json` and `agents/` |
| Board orchestration | `GITHUB_ORCHESTRATION.md`, `scripts/gh_project_sync.py` |
| Durable product facts | `products/<name>.md`, one pack per product, loaded only for that product ([products/README.md](products/README.md)) |
| Find a skill for a task | `python3 scripts/find_skill.py <keyword>` |
| Measure agent behaviour | [evals/README.md](evals/README.md), `scripts/run_scenarios.py` |
| Anything about a script | [scripts/README.md](scripts/README.md) |

## Validation before a PR

```bash
python3 -m pytest tests/ -q
python3 scripts/audit_skills.py
python3 scripts/check_version.py
python3 scripts/docs.py check
python3 scripts/check_writing.py <changed .md files>
```

CI runs all of these plus the generated-file drift checks. Install the same
checks locally once per clone:

```bash
git config core.hooksPath .githooks
```

When a change alters what agents are told or how they work, run the scenario
smoke set before and after:

```bash
python3 scripts/run_scenarios.py --smoke
```

Put the before-and-after table in the PR description.
