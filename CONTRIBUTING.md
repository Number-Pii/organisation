# Contributing to the Number Pii Organisation Toolkit

All changes require review by the relevant department head. Structural changes need sign-off from the CEO or Chief of Staff.

---

## Branch Naming

Create a branch from `main` using the correct prefix:

| Prefix | When to use |
|--------|------------|
| `feature/` | New roles, skills, protocol steps, scripts |
| `fix/` | Corrections to existing content |
| `chore/` | Maintenance — version bumps, dependency updates, CI changes |
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

**Never push directly to `main`.** See [Version Control Discipline](CLAUDE.md#version-control-discipline).

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
2. Add a `SKILL.md` file (required) with the full frontmatter block — see the schema below
3. Optionally add `scripts/`, `examples/`, or `resources/` subdirectories
4. Reference the skill in the relevant role file(s) if appropriate
5. Run `python3 scripts/audit_skills.py` to confirm the skill is detected and the frontmatter validates

### SKILL.md frontmatter schema

Every new skill MUST ship with all nine fields — the five base fields (present on every legacy skill) plus the four extension fields used by the scoped-discovery tooling (`scripts/find_skill.py`) and the coverage auditor.

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
size_class: m                     # xs <50 · s 50–199 · m 200–499 · l 500–999 · xl 1000+ lines
summary: "One-line answer to 'what's this skill for' — ≤150 chars, surfaced by find_skill.py."
detail_sections:
  - When to Use
  - Core Concepts
  - Examples
---
```

#### Rules
- `domain` is validated against `Teams/skills/CATEGORIES.md`. If your skill doesn't fit an existing domain, open the discussion in your PR — do not invent a new value.
- `size_class` must match the actual line count band; the auditor warns on mismatches.
- `summary` is what `find_skill.py` surfaces in result rows — make it informative, not a persona opener.
- `detail_sections` lists your top-level `## ` headers, so a loader can expand sections on demand.

#### Bootstrap with the generator

`scripts/generate_skill_frontmatter.py` proposes all four extension fields from an existing SKILL.md:

```bash
# Preview the proposed block
python3 scripts/generate_skill_frontmatter.py Teams/skills/my-new-skill/SKILL.md

# Write it in place (overwrites the four extension fields if already present)
python3 scripts/generate_skill_frontmatter.py Teams/skills/my-new-skill/SKILL.md --write
```

Always human-review the proposal: domain lookup falls back to `uncategorised` for skills not yet in CATEGORIES.md, and the summary is taken from the first sentence of `description` — tighten or rewrite it if the first sentence is a persona opener or too terse.

#### Legacy skills

Existing skills without the four extension fields still validate (the auditor treats extensions as opt-in during backfill). Coverage is reported in `scripts/audit_skills.py` output and is being expanded domain-by-domain — no single-PR mandate.

---

## Bumping the Version

1. Update `VERSION` with the new version number
2. Add a new section at the top of `CHANGELOG.md` with the changes and migration notes
3. If the protocol changed, update the `_Version:` line in both `CLAUDE.md` and `GEMINI.md`
4. Run `python3 scripts/check_version.py` to confirm everything is in sync

### Version types

| Bump | When |
|------|------|
| PATCH (`x.x.1`) | Wording fixes, role/skill updates — no protocol changes |
| MINOR (`x.1.0`) | New protocol steps, new features, significant additions |
| MAJOR (`1.0.0`) | Breaking changes to Initialize Protocol or doc/ template structure |

---

## Keeping CLAUDE.md and GEMINI.md in Sync

`CLAUDE.md` is the **source of truth**. `GEMINI.md` is generated from it by `scripts/sync_ai_context.py` — do not edit `GEMINI.md` by hand.

### Why both files exist
Claude Code auto-loads `CLAUDE.md`; Gemini CLI auto-loads `GEMINI.md`. The toolkit must work in both, so both files must be present.

### How sync works
Edit `CLAUDE.md`, then run:

```bash
python3 scripts/sync_ai_context.py
```

The script rewrites `GEMINI.md` with the two known substitutions:
- Tool-name references (`CLAUDE.md` → `GEMINI.md`, `Claude Code` → `Gemini CLI`) in the acknowledgement list and Step 7 handover pointer
- Sync-comment header

CI and the pre-commit hook run the same script and fail the build if drift is detected (`python3 scripts/sync_ai_context.py --check`).

---

## Cache-safe vs Volatile Blocks

Some parts of the toolkit change often; others barely change at all. Marking the stable blocks with a `<!-- CACHE_BOUNDARY -->` HTML comment gives contributors a clear "don't churn this without good reason" signal and gives future tooling a hook to place prompt-cache breakpoints.

**This is a contributor convention, not a live Claude Code directive.** Claude Code does not parse these sentinels today — Anthropic's prompt cache operates at the SDK level via explicit `cache_control` breakpoints on API requests, not by scanning markdown. The sentinels exist so that (a) contributors treat the marked blocks as stable by default, and (b) any future wrapper that reads them can translate them into real cache breakpoints without a schema change.

### Where the sentinels sit today

**Cache-safe** (end with `<!-- CACHE_BOUNDARY -->`):

- `CLAUDE.md` — end of the Non-Negotiable Standards section
- `GEMINI.md` — same placement (propagates automatically via `sync_ai_context.py`)
- `Teams/organisation.md` — end of file
- `Teams/philosophy.md` — end of file

**Volatile** (no sentinel — expect churn):

- `doc/project-brief.md`, `doc/team-assignment.md`, `doc/workflow.md`, `doc/handover/**` — per-project, rewritten every engagement
- `Agent Skills` sections inside role files — curated list changes as new skills land
- `CHANGELOG.md`, `VERSION` — bumped every release
- Individual `Teams/skills/**/SKILL.md` — edited as skills evolve

### When editing a cache-safe block

Churning a cache-safe block invalidates downstream cache for every context that loads it. Before editing one:

1. Prefer a smaller, additive change over a rewrite
2. Confirm the change is genuinely terminal — not "nice to have" wording
3. Expect that the next session's warm cache is lost; this is fine for binding rules, wasteful for cosmetics

`sync_ai_context.py` preserves HTML comments, so sentinels in `CLAUDE.md` appear in `GEMINI.md` automatically — never hand-edit `GEMINI.md` to add or remove one.

---

## Why the Mandatory Reading Protocol Exists

Past sessions have skipped project context files, expanded scope without permission, pushed directly to `main`, and created ad-hoc troubleshooting docs inside `doc/`. Every one of those failures traced back to an AI assistant treating the protocol as optional reading.

The Mandatory Reading Protocol in `CLAUDE.md` / `GEMINI.md` — and every Non-Negotiable Standard under it — is written as a hard rule precisely because soft guidance produced repeated regressions. When tempted to compress further, remember: the rules are short because they are terminal, not because they are flexible.
