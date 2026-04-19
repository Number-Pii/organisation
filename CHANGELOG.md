# Changelog

All notable changes to the Number Pii Organisation Toolkit are documented here.

Version format: `MAJOR.MINOR.PATCH`
- **MAJOR** — breaking changes to the Initialize Protocol or doc/ template structure
- **MINOR** — new features, new steps, significant additions to CLAUDE.md / GEMINI.md
- **PATCH** — wording fixes, role file updates, skill additions

> **Safe to update?** Any version bump that is MINOR or PATCH will not break existing projects.
> A MAJOR bump means the Initialize Protocol changed in a way that may affect new sessions —
> your existing `doc/` files are always safe, but read the migration notes before re-initializing.

---

## [3.6.0] — 2026-04-19

### Added
- **Scoped skill discovery** — new `scripts/find_skill.py` returns matching skill
  names only (no SKILL.md content loaded). Step 3 of the Initialize Protocol and
  the Skills Directory section in `CLAUDE.md` / `GEMINI.md` now point to it as
  the preferred scan before loading any full skill definition. (PR #4, PR #5)
- **Extended SKILL.md frontmatter schema** for lazy-loading. Four new fields —
  `domain`, `size_class`, `summary`, `detail_sections` — are now required on all
  new skills. `find_skill.py` surfaces `summary` in result rows and prefers
  frontmatter `domain` over the CATEGORIES.md lookup. (PR #6)
- **`scripts/generate_skill_frontmatter.py`** — helper that proposes the four
  extension fields from an existing SKILL.md and supports in-place `--write`. (PR #6)
- **`scripts/audit_skills.py`** extended with a zero-dep YAML subset parser, an
  opt-in validator for the four extension fields, and a new coverage stat
  (`Skills with extended frontmatter: N/1294`). (PR #6)
- **16 pilot skills** extended with the new frontmatter: `project-development`,
  `internal-comms`, `analytics-product`, `api-design-principles`,
  `writing-plans`, `security-audit`, `aws-skills`,
  `javascript-testing-patterns`, `react-best-practices`, `workflow-automation`,
  `postgresql`, `cloud-architect`, `backend-dev-guidelines`,
  `software-architecture`, `e2e-testing`, `fp-refactor`. (PR #6)
- **`<!-- CACHE_BOUNDARY -->` sentinel convention** on stable blocks: end of
  Non-Negotiable Standards in `CLAUDE.md` / `GEMINI.md`, end of
  `Teams/organisation.md`, end of `Teams/philosophy.md`. Framed as a contributor
  "don't churn this without good reason" signal and a hook for future
  prompt-cache tooling — not a live Claude Code directive. New "Cache-safe vs
  Volatile Blocks" section in `CONTRIBUTING.md`. (PR #7)
- **Token-efficiency optimisations** across the toolkit (items 1–5, 8, 10 of the
  Token Efficiency & Context Window Optimization close-out plan). (PR #3)

### Changed
- `CONTRIBUTING.md` "Adding a New Skill" now documents the full nine-field
  frontmatter contract (five base + four extension fields) and the
  `generate_skill_frontmatter.py` bootstrap workflow.
- **Protocol version** recorded as 2.6 in `CLAUDE.md` / `GEMINI.md`. The 2.5 → 2.6
  transition was introduced in PR #3 without a corresponding `VERSION`/CHANGELOG
  bump at the time; this release formalises it.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- New skills added to `Teams/skills/` MUST now include all four extension
  fields. Use `python3 scripts/generate_skill_frontmatter.py <path> --write`
  to bootstrap the proposal, then human-review `summary` and `detail_sections`
  before committing.
- Existing skills without the extension fields remain valid; the extension is
  opt-in during backfill.

---

## [3.5.0] — 2026-04-12

### Added
- **Mandatory Reading Protocol** at the top of `CLAUDE.md` and `GEMINI.md`. Declares both
  files and the project `doc/` folder as a binding contract, requires a session-start
  acknowledgement that the core context files have been read, and forbids acting without
  them. Directly addresses AI sessions that had been skipping project context.
- **Mandatory Context Files** added to Non-Negotiable Standards in `CLAUDE.md` and
  `GEMINI.md`. Lists the required `doc/` files and makes clear that their instructions
  override AI defaults and training priors.
- `init_project.py` now scaffolds a `CLAUDE.md` and `GEMINI.md` in the consuming project
  root that carry the same Mandatory Reading Protocol and the inherited Non-Negotiable
  Standards — so every new AI session in a scaffolded project is bound by the rules
  immediately, without depending on the toolkit being present.
- Protocol version bumped to 2.5.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- To get the new project-level `CLAUDE.md` / `GEMINI.md` in an existing project, re-run
  `init_project.py` against that project — existing `doc/` files are preserved (the
  scaffolder skips files that already exist).

---

## [3.4.0] — 2026-03-30

### Added
- **Version Control Discipline** added to Non-Negotiable Standards in `CLAUDE.md` and `GEMINI.md`.
  Mandates branch-based workflow, bans direct pushes to `main`, and requires `doc/version_control.md`
  to be read before any git operation. Applies to all team members including AI agents.
- Protocol version bumped to 2.4.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you re-initialize an existing project session, the version control discipline rules will apply.

---

## [3.3.0] — 2026-03-27

### Changed
- Recommended consumption pattern is now **gitignored local clone**: clone the toolkit into
  your project root and add `organisation/` to `.gitignore`. The toolkit stays local and
  updatable but is never committed to the consuming project.
- Step 4 of the Initialize Protocol updated to show the simpler `--output-dir .` form
  (works when toolkit is gitignored inside the project root). Protocol version bumped to 2.2.

### Removed
- Static copy pattern (Pattern B) removed from documentation — strictly inferior to gitignored clone.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you had `organisation/` tracked as files in a consuming project, remove it:
  `git rm -r organisation/ && echo "organisation/" >> .gitignore`
  then re-clone: `git clone https://github.com/Number-Pii/organisation.git organisation`

---

## [3.2.0] — 2026-03-27

### Changed
- Step 4 of the Initialize Protocol now requires `--output-dir` pointing to the consuming
  project root. Prevents `doc/` being created inside the organisation toolkit by mistake.
  Updated in both `CLAUDE.md` and `GEMINI.md` (protocol version 2.1).

### Added
- `scripts/init_project.py` safety guard: exits with a clear error if `--output-dir`
  resolves to the organisation toolkit root.
- `README.md`: new "Using This Toolkit in Your Projects" section documenting two consumption
  patterns (git submodule and static copy) and the three-step fix for existing projects.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you re-run `init_project.py`, you must now supply `--output-dir`.

---

## [3.1.0] — 2026-03-26

### Added
- **Step 6 — Scope Discipline** added to the Initialize Protocol in CLAUDE.md and GEMINI.md.
  Enforces `doc/project-brief.md` as the hard boundary for all project work. Existing projects
  are unaffected — this only applies when starting new tasks or new AI sessions.
- **Mandatory Handover Rule** added to Step 7. Clarifies that no task is complete until handover
  notes are updated. No changes to the `doc/` file structure — existing handover files are compatible.

### Changed
- Welcome message corrected: "Welcome to Number Pii" (was "Welcome, Number Pii").

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you re-initialize an existing project session, the stricter scope and handover rules will apply.

---

## [3.0.0] — 2026-03-25

### Added
- Full skill linking across all 53 role files: Core Skills, Technical Skills, and Agent Skills layers.
- `Teams/skills/` directory with 1,294 AI skill modules.
- `scripts/audit_skills.py` — skill coverage auditor.
- `GEMINI.md` — Gemini CLI counterpart to CLAUDE.md (identical content).
- `scripts/README.md` — script usage documentation.

### Changed
- Initialize Protocol expanded from 5 steps to 7 steps (added Step 6 and Step 7).
- `scripts/init_project.py` updated with richer templates including Decision Authority Matrix
  and Completion Criteria sections.

### Migration Notes
- **MAJOR version**: If upgrading from 2.x, the Initialize Protocol has new steps.
- Existing `doc/` files created with 2.x templates remain valid — no reformatting needed.
- New projects will get the richer 3.x templates automatically.

---

## [2.0.0] — 2026-02-01

### Added
- Initial `scripts/init_project.py` scaffolder.
- `doc/` folder structure: project-brief, team-assignment, workflow, version_control, handover.
- Consolidated handover and department handover note templates.

---

## [1.0.0] — 2025-12-01

### Added
- Initial organisation structure: 53 roles across 6 departments.
- `Teams/organisation.md` — master org chart, delegation model, approval authority matrix.
- `CLAUDE.md` with Initialize Protocol (Steps 1–5).
