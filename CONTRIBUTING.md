# Contributing to the Number Pii Organisation Toolkit

All changes require review by the relevant department head. Structural changes need sign-off from the CEO or Chief of Staff.

---

## Branch Naming

Create a branch from `main` using the correct prefix:

| Prefix | When to use |
|--------|------------|
| `feature/` | New roles, skills, protocol steps, scripts |
| `fix/` | Corrections to existing content |
| `chore/` | Maintenance: version bumps, dependency updates, CI changes |
| `hotfix/` | Critical fixes that need immediate attention |

Example: `chore/update-skill-count`

---

## Commit Messages

Use conventional commit format:

```
type(scope): short description

types: feat | fix | docs | style | refactor | test | chore
```

Examples:
- `feat(skills): add kubernetes-observability skill`
- `fix(roles): correct CTO reporting line`
- `chore(scripts): bump audit output format`

---

## Pull Requests

1. Create your branch from `main`
2. Make your changes
3. Run validation before pushing:
   ```bash
   python3 scripts/audit_skills.py        # check skill coverage
   python3 scripts/check_version.py       # check version sync
   ```
4. Open a PR with a clear description of **what** changed and **why**
5. Get approval before merging

**Never push directly to `main`.** Branch protection enforces it; see [AGENTS.md](AGENTS.md#boundaries).

---

## Adding a New Role

1. Create a `.md` file in the appropriate `Teams/[department]/` folder
2. Follow the existing role file structure:
   - Position Details (department, reports to, direct reports, employment type)
   - Role Summary
   - Core Skills (with inline `@skill-name` references)
   - Technical Skills (with inline `@skill-name` references)
   - Project Involvement table
   - Approval Authority
   - Agent Skills (curated `@skill-name` list)
3. Update `Teams/organisation.md` to include the new role in the org chart
4. Update `README.md` department table
5. Run `python3 scripts/audit_skills.py` to verify all `@skill` references resolve

---

## Adding a New Skill

The library is deliberately small. A skill earns its place only when it gives a
frontier model something the model lacks:

- working bundled scripts or assets (the document skills, `webapp-testing`, `mcp-builder`)
- tool- or API-specific knowledge that models get wrong or that changes quickly
- a Number Pii process (`github-project-orchestrator`)
- the one canonical approach to a topic where consistency across agents matters

General expertise does not qualify: "You are an expert X" adds nothing a current
model does not already bring.

1. Create `Teams/skills/<name>/SKILL.md` with the frontmatter below. `name` and
   `description` follow the open Agent Skills convention, so native skill loaders
   in Claude Code and Codex can read the file too.
2. Show that it helps. Add a task to `evals/tasks/` and run it bare and with the
   skill on both runners (`python3 scripts/run_evals.py --runner claude`, then
   `--runner codex`). Put the verdict in the PR.
3. Reference it from the role files where it applies.
4. Run `python3 scripts/build_skills_index.py` and `python3 scripts/audit_skills.py`,
   and commit the regenerated index files.

### SKILL.md frontmatter

```yaml
---
name: my-new-skill                # kebab-case, matches the folder name
description: "What the skill does and when to use it."
risk: low                         # low | medium | high, from reading every file in the skill
source: community                 # community | vendor | internal | <attribution>
date_added: "2026-09-23"
last_reviewed: "2026-09-23"       # re-read during the quarterly review
tier: curated
domain: "Backend & APIs"          # one of the headings in Teams/skills/CATEGORIES.md
size_class: m                     # xs <50 · s 50-199 · m 200-499 · l 500-999 · xl 1000+ lines
summary: "One line surfaced by find_skill.py, 150 characters or fewer."
detail_sections:
  - When to Use
canonical: true                   # optional: the preferred skill for its topic
requires: claude-code             # optional: only when it depends on one agent's tools
---
```

`audit_skills.py` fails on a skill without a `low`, `medium`, or `high` risk and a
`last_reviewed` date, on frontmatter drift, and on any `@skill` reference that does
not resolve.

### Removing a skill

Open a PR that states why: superseded, stale, or no measurable benefit. Removed
skills stay recoverable. The full 1,291-skill library as of 3.20 is tagged
`v3-skills-full`; restore one with
`git checkout v3-skills-full -- Teams/skills/<name>`, then review it as a new skill.

### Generated skill indexes

`Teams/skills/skills-index.json` and `Teams/skills/CATEGORIES.md` are generated from skill frontmatter by `scripts/build_skills_index.py`; CI fails if they drift. Never edit them by hand: change the frontmatter, regenerate, and commit both. Domain description lines in CATEGORIES.md carry over from the previous generation, so a brand-new domain gets its one-line description edited once, then the generator preserves it.

The same rule covers the org data: `Teams/org.json` (from `scripts/build_org.py`) and `agents/np-*.md` (from `scripts/build_agents.py`) are generated from the role files under `Teams/`. Edit the role markdown, regenerate, commit together. The plugin manifest version in `.claude-plugin/plugin.json` must match `VERSION`; `check_version.py` enforces it.

---

## Tests and Templates

CI runs the pytest suite in `tests/` on every push and PR (`python3 -m pytest tests/ -q`; see `tests/README.md`). Two conventions matter when contributing:

- **Scaffold wording lives in `templates/*.md`, not in Python.** `scripts/init_project.py` renders those files with `string.Template`; edit the markdown, never inline strings in the script. Level-dependent content (quality gates, PR rules, release process) comes from the `LEVELS` table in the script.
- **Template changes must regenerate the goldens.** The suite compares scaffold output byte for byte against `tests/golden/`. After an intentional template edit, run `python3 tests/generate_goldens.py`, review `git diff tests/golden` as part of your PR, and commit the result.

Shared script logic (currently the frontmatter parser) lives in `scripts/lib/`; import it from there rather than from another script.

---

## Changelog and Releases

Feature and fix PRs never edit `VERSION`, `CHANGELOG.md`, or the plugin manifest version.
Each PR adds one changelog fragment under `changes/` instead, named after its branch; CI
fails a PR without one. That keeps parallel PRs from colliding on the same lines.
[changes/README.md](changes/README.md) has the fragment format.

A release is its own PR on a `chore/release-X.Y.Z` branch: run
`python3 scripts/release.py`, which compiles the fragments into a `CHANGELOG.md`
section, bumps `VERSION` and `.claude-plugin/plugin.json`, and deletes the fragments.
`python3 scripts/check_version.py` confirms the three stay in sync. Consumer clones
follow release tags, so merged but unreleased work on `main` never reaches them early.

### Version types

| Bump | When |
|------|------|
| PATCH (`x.x.1`) | Wording fixes, role/skill updates; no protocol changes |
| MINOR (`x.1.0`) | New protocol steps, new features, significant additions |
| MAJOR (`1.0.0`) | Breaking changes to Initialize Protocol or doc/ template structure |

---

## Instruction Files

Two sets of agent instructions live here, and they are kept apart on purpose:

- **This repository's own:** `AGENTS.md` at the root, written for whoever maintains the
  toolkit. `CLAUDE.md` and `GEMINI.md` are stubs that import it with `@AGENTS.md`, so
  there is one file to edit and nothing to sync.
- **What every consuming project is told:** the managed block in
  `templates/agents-block.md`. `init_project.py` places it in each new project's
  `AGENTS.md`; `sync_context.py` refreshes it in existing ones. Keep it under about 100
  lines, and give every rule in it a stated reason. It is loaded into every session of
  every project, so each line costs context everywhere.

Write instructions as outcomes and boundaries, not step-by-step procedures. Say what must
be true and why, and leave the method to the model. Before changing the block, run the
scenario smoke set against the current version and against your branch, then put both
tables in the PR (`python3 scripts/run_scenarios.py --smoke --toolkit-ref <ref>`).

### Pre-commit hook

The hook lives in `.githooks/pre-commit`. It runs the version check, the plugin
packaging check, the documentation graph check (`scripts/docs.py check`), and the
writing validator on staged markdown. Install it once per clone:

```bash
git config core.hooksPath .githooks
```

### Release tagging

CI tags releases automatically: when a version bump merges to `main`, the
`tag-release` job creates and pushes an annotated `v$(cat VERSION)` tag if one
does not exist yet. No manual step is needed on the normal path.

If CI is unavailable, or a historical release needs a retroactive tag, the
manual fallback is:

```bash
git tag -a v3.13.0 -m "Release 3.13.0"
git push origin v3.13.0
```

---

## Keeping the Toolkit Current

Models improve faster than this toolkit does, so parts of it expire. Review it once a
quarter and after any major model release from Anthropic or OpenAI:

1. **Measure.** Run the full scenario suite on the current models
   (`python3 scripts/run_scenarios.py --all --repeat 3`) and compare it with the latest
   scorecard in `evals/scorecards/`.
2. **Prune instructions.** For every rule in `templates/agents-block.md` and `AGENTS.md`,
   ask whether current models still need it to behave well. A rule that no longer
   changes behaviour, or that no one can give a reason for, goes.
3. **Re-review skills.** Any skill whose `last_reviewed` date is more than two quarters
   old gets re-read. Keep it if it still adds something a frontier model lacks;
   otherwise remove it.
4. **Record the outcome.** Put the findings and the new scorecard in the release PR.
