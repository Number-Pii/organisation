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

1. Create a folder in `Teams/skills/` with a kebab-case name (e.g. `my-new-skill/`)
2. Add a `SKILL.md` file (required) with the full frontmatter block; see the schema below
3. Optionally add `scripts/`, `examples/`, or `resources/` subdirectories
4. Reference the skill in the relevant role file(s) if appropriate
5. Run `python3 scripts/audit_skills.py` to confirm the skill is detected and the frontmatter validates

### SKILL.md frontmatter schema

Every new skill MUST ship with all nine fields; the five base fields (present on every legacy skill) plus the four extension fields used by the scoped-discovery tooling (`scripts/find_skill.py`) and the coverage auditor.

```yaml
---
# Base fields (required on every skill)
name: my-new-skill                # kebab-case, must match folder name
description: "One paragraph describing what the skill does and when to invoke it."
risk: none                        # none | low | medium | high | unknown
source: community                 # community | vendor | internal | <attribution>
date_added: "2026-04-18"          # ISO date, quoted

# Extension fields (required on all new skills)
domain: "Backend & APIs"          # MUST match one of the 17 headings in Teams/skills/CATEGORIES.md exactly
size_class: m                     # xs <50 · s 50-199 · m 200-499 · l 500-999 · xl 1000+ lines
summary: "One-line answer to 'what's this skill for'; ≤150 chars, surfaced by find_skill.py."
detail_sections:
  - When to Use
  - Core Concepts
  - Examples
---
```

#### Rules
- `domain` is validated against `Teams/skills/CATEGORIES.md`. If your skill doesn't fit an existing domain, open the discussion in your PR; do not invent a new value.
- `size_class` must match the actual line count band; the auditor warns on mismatches.
- `summary` is what `find_skill.py` surfaces in result rows; make it informative, not a persona opener.
- `detail_sections` lists your top-level `## ` headers, so a loader can expand sections on demand.

#### Bootstrap with the generator

`scripts/generate_skill_frontmatter.py` proposes all four extension fields from an existing SKILL.md:

```bash
# Preview the proposed block
python3 scripts/generate_skill_frontmatter.py Teams/skills/my-new-skill/SKILL.md

# Write it in place (overwrites the four extension fields if already present)
python3 scripts/generate_skill_frontmatter.py Teams/skills/my-new-skill/SKILL.md --write
```

Always human-review the proposal: domain lookup falls back to `uncategorised` for skills not yet in CATEGORIES.md, and the summary is taken from the first sentence of `description`; tighten or rewrite it if the first sentence is a persona opener or too terse.

#### Legacy skills

Existing skills without the four extension fields still validate (the auditor treats extensions as opt-in during backfill). Coverage is reported in `scripts/audit_skills.py` output and is being expanded domain-by-domain; no single-PR mandate.

### Skill tiers and promotion

Skills are third-party instructions injected into agent context, so the library is a supply chain and the tier field is its review gate:

| Tier | Meaning | Search visibility |
|------|---------|-------------------|
| `curated` | Reviewed and referenced by at least one role file | Default (`find_skill.py`) |
| `standard` | Unreviewed community content (the default when `tier` is absent) | `--all` or `--tier standard` |
| `archive` | Off-charter or superseded; kept for reference | `--tier archive` only |

`canonical: true` marks the preferred skill when several cover the same topic (one per cluster); it sorts first in search and in CATEGORIES.md.

**Promotion checklist (standard to curated).** All five in one PR:

1. Read the full SKILL.md and any bundled files; confirm the content does what the summary claims and nothing else.
2. Set `risk:` to a reviewed value (`low`, `medium`, or `high` with a note); `unknown` blocks promotion, and the audit flags curated skills left at `unknown`.
3. Confirm `source:` records where the content came from.
4. Reference the skill from at least one role file section, or record in the PR why it is curated without a role.
5. Set `tier: curated`, run `python3 scripts/build_skills_index.py`, and commit the regenerated index files.

Demotion to `archive` needs only a PR stating the reason (off-charter, superseded by a canonical, licence concern).

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
