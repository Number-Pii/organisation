# Changelog

All notable changes to the Number Pii Organisation Toolkit are documented here.

Version format: `MAJOR.MINOR.PATCH`
- **MAJOR**: breaking changes to the Initialize Protocol or doc/ template structure
- **MINOR**: new features, new steps, significant additions to CLAUDE.md / GEMINI.md
- **PATCH**: wording fixes, role file updates, skill additions

> **Safe to update?** Any version bump that is MINOR or PATCH will not break existing projects.
> A MAJOR bump means the Initialize Protocol changed in a way that may affect new sessions;
> your existing `doc/` files are always safe, but read the migration notes before re-initializing.

---

## [3.12.1]: 2026-06-10

### Changed
- **Legacy dash sweep.** All em dashes and en dashes removed from maintained toolkit
  prose, bringing the whole repository in line with the Writing Style standard:
  role files (Agent Skills separators now use colons), `organisation.md`,
  `philosophy.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `INITIALIZE.md`,
  `CLAUDE.md`, the role template, script docstrings, and script output strings.
- Role display names with em dash separators now use parentheses: "Product Manager
  (Future Products)", "Principal Consultant (Digital Transformation)", "Principal
  Consultant (Technology Strategy)", "Senior Software Engineer(s) (Custom)".
- The only remaining dash characters are the rule statements that name them (in
  `CLAUDE.md`, `WRITING.md`, `scripts/README.md`), HTML comments (exempt from prose
  scanning), and the vendored `Teams/skills/` modules, which stay out of scope.
- `GEMINI.md`, `AGENTS.md`, and `scripts/audit_report.md` regenerated. No rule or
  protocol content changed; this is a wording-only PATCH release.

## [3.12.0]: 2026-06-10

### Added
- **Writing Standards Framework.** Writing quality is now a first-class, enforceable
  system component rather than a single style rule:
  - **`WRITING.md`** at the toolkit root (on-demand, model-neutral, binding): core
    directive (prose indistinguishable from a skilled human writer), readability
    targets (Flesch 30 to 40 professional, 50 to 65 marketing), vocabulary and
    structural rules, a machine-readable banned-phrases list, banned AI patterns,
    document-type calibration for technical / product / consultancy / marketing /
    internal writing, the governance model, and the compliance loop.
  - **`scripts/check_writing.py`**: automated validator. FAILs on em/en dashes,
    banned phrases (read live from `WRITING.md`), and repeated sentence openers;
    WARNs on readability outside target, low sentence variety, and high passive
    voice. Exit codes suit editorial gates and CI.
  - **Governance:** Head of Content & SEO owns the standard; Senior Content
    Strategist is the editorial reviewer for client-facing deliverables. Both role
    files updated.
  - **Enforcement embeds:** a Writing quality gate added to all four classification
    levels (self-check at Level 1 up to mandatory recorded editorial sign-off at
    Level 4); scaffolded context contracts gain standard #8 (Writing Standards).

### Changed
- The Writing Style standard in `CLAUDE.md` now bans en dashes as well as em dashes,
  requires `WRITING.md` to be read before substantial prose work, and names the
  validator and the owners. `WRITING.md` joins the binding-contract list.
- All scaffolder templates in `init_project.py` swept clean of em and en dashes so
  newly scaffolded docs pass the validator from day one.
- Remaining en dashes in `CLAUDE.md` and `INITIALIZE.md` replaced with hyphens.
- Protocol version bumped to 2.12 in `CLAUDE.md`; `GEMINI.md` and `AGENTS.md` regenerated.

## [3.11.0]: 2026-06-10

### Added
- **Software Delivery Lifecycle.** `INITIALIZE.md` now defines six stages (Discovery,
  Planning, Implementation, Verification, Deployment, Operations) with their outputs,
  mapped onto the existing init steps and doc files rather than added as a parallel
  framework. Steps 2 to 2c complete Discovery; Steps 3 to 5 complete Planning; the
  scaffolded doc files carry Stages 3 to 6. Applies to products, client services, and
  consultancy alike; consultancy outputs adapt but the stages and gates still apply.
- Step 8 closure checklist: operations ownership (monitoring, support, maintenance)
  must be recorded in `consolidated_handover.md` before a project closes.

### Changed
- `init_project.py` workflow template: the Task Breakdown is now organised by lifecycle
  stage (Stages 2 to 6) instead of unnamed phases, with the quality gates as the exit
  criteria for Verification, and "all quality gates pass" added to Completion Criteria.
- Protocol version bumped to 2.11 in `CLAUDE.md`; `GEMINI.md` and `AGENTS.md` regenerated.

## [3.10.0]: 2026-06-10

### Added
- **`INITIALIZE.md`** at the toolkit root: the full Initialize Protocol (Steps 1 through 8)
  now lives in its own model-neutral file, loaded on demand when the user says
  "initialize". It carries the same binding force as `CLAUDE.md` and ends with a
  `CACHE_BOUNDARY` sentinel.

### Changed
- **Token optimisation: always-loaded context cut by 54%.** `CLAUDE.md` shrank from
  19.5KB to 9.0KB (with `GEMINI.md` and `AGENTS.md` matching) by moving the Initialize
  Protocol to `INITIALIZE.md`, merging the overlapping Skill Linking / Quick Start /
  Skills Directory / Finding the Right Role sections into one Skills section, and
  stating the non-negotiable preamble once instead of repeating it under each standard.
  Total context for an init session is unchanged; every other session loads ~10.5KB less.
- No rule was removed or weakened: all six Non-Negotiable Standards keep their full
  operative bullets, and the Mandatory Reading Protocol gains an explicit instruction
  to read `INITIALIZE.md` in full when the protocol is triggered (never run it from memory).
- `sync_ai_context.py`: the Step 7 handover-pointer substitution was retired because the
  protocol body is now model-neutral; only the acknowledgement-line substitution remains.
- The trigger list now includes "initialize AGENTS.md" (previously only CLAUDE/GEMINI).
- `CONTRIBUTING.md` sync and cache-boundary docs updated; `README.md` repository tree
  updated. The user-facing init flow is unchanged, so this is a MINOR bump.
- Protocol version bumped to 2.10 in `CLAUDE.md`; `GEMINI.md` and `AGENTS.md` regenerated.

## [3.9.0]: 2026-06-10

### Added
- **Project Classification Framework.** New Step 2c in the Initialize Protocol: every
  project is classified Level 1 (Simple Task) to Level 4 (Large-Scale Engineering) and
  the level is confirmed with the user before team assignment. The level sets the depth
  of documentation, architecture, testing, security, and review for the whole project.
- `init_project.py --level {1,2,3,4}` (default 2). The scaffolder now writes the
  classification into `project-brief.md`, level-matched quality gates into
  `workflow.md`, and a suggested branching strategy into `version_control.md`. The
  generated `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` context contracts state the level.
- `doc/architecture.md` template, created at Level 3 and 4 only: system overview,
  components, data model, NFRs, failure modes, and decision records. At Level 4 the
  failure-mode and decision-record sections are mandatory.
- Step 8 closure checklist now requires all quality gates for the project's level
  to pass before a project is marked complete.

### Changed
- Step 3 team-size guide now keys off the classification level (Level 1: 1-3 roles
  through Level 4: full team assignment).
- `scripts/README.md` documents `--level` and `--existing`.
- Protocol version bumped to 2.9 in `CLAUDE.md`; `GEMINI.md` and `AGENTS.md` regenerated.

## [3.8.0]: 2026-06-10

### Added
- **Governance: Two Layers.** `CLAUDE.md` and `Teams/organisation.md` now state explicitly that
  Number Pii is owned and operated by its co-founders, Olatunbosun Iyare and Destiny Ihejirika,
  who hold final decision-making authority. All virtual roles (including executive titles) hold
  delegated execution authority only. The org chart and Approval Authority Matrix now show the
  founders at the top.
- **Product Neutrality policy.** All Number Pii products are treated equally; no product is
  flagship, primary, or priority unless the founders explicitly instruct otherwise. Stated in
  `CLAUDE.md`, `Teams/organisation.md`, and `README.md`.

### Changed
- `Senior-Product-Manager-ThirtyX.md` renamed to `Senior-Product-Manager.md`; the role is now
  product neutral and works on any assigned product.
- `CEO-Founder.md` renamed to `CEO.md`; the virtual CEO reports to the founders (not a fictional
  Board of Directors) and no longer claims final decision-making authority.
- All "Thirty X" references in role files, `organisation.md`, `philosophy.md`, `README.md`, and
  the `init_project.py` team-assignment template replaced with product-neutral wording.
- `Chief-of-Staff.md` Board references replaced with founder support duties.
- Protocol version bumped to 2.8 in `CLAUDE.md`; `GEMINI.md` and `AGENTS.md` regenerated.

## [3.7.0]: 2026-05-03

### Added
- **OpenAI Codex support**: `AGENTS.md` is now generated alongside `GEMINI.md` from
  `CLAUDE.md` via `scripts/sync_ai_context.py`. OpenAI Codex auto-loads `AGENTS.md`,
  giving all three major AI coding assistants (Claude Code, Gemini CLI, Codex) full
  access to the toolkit context without any manual setup.
- `README.md` updated with Codex in the cross-platform support section and
  `initialize AGENTS.md` as a third initialize command example.

### Changed
- `scripts/sync_ai_context.py` refactored to support multiple targets. Both
  `GEMINI.md` and `AGENTS.md` are written (or checked) in a single run.
- CI step now validates both generated files are in sync with `CLAUDE.md`.
- Protocol version bumped to 2.7 in `CLAUDE.md`.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- Run `python3 scripts/sync_ai_context.py` once after pulling to generate `AGENTS.md`.

---

## [3.6.0]: 2026-04-19

### Added
- **Scoped skill discovery**: new `scripts/find_skill.py` returns matching skill
  names only (no SKILL.md content loaded). Step 3 of the Initialize Protocol and
  the Skills Directory section in `CLAUDE.md` / `GEMINI.md` now point to it as
  the preferred scan before loading any full skill definition. (PR #4, PR #5)
- **Extended SKILL.md frontmatter schema** for lazy-loading. Four new fields
  (`domain`, `size_class`, `summary`, `detail_sections`) are now required on all
  new skills. `find_skill.py` surfaces `summary` in result rows and prefers
  frontmatter `domain` over the CATEGORIES.md lookup. (PR #6)
- **`scripts/generate_skill_frontmatter.py`**: helper that proposes the four
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
  prompt-cache tooling, not a live Claude Code directive. New "Cache-safe vs
  Volatile Blocks" section in `CONTRIBUTING.md`. (PR #7)
- **Token-efficiency optimisations** across the toolkit (items 1-5, 8, 10 of the
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

## [3.5.0]: 2026-04-12

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
  Standards, so every new AI session in a scaffolded project is bound by the rules
  immediately, without depending on the toolkit being present.
- Protocol version bumped to 2.5.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- To get the new project-level `CLAUDE.md` / `GEMINI.md` in an existing project, re-run
  `init_project.py` against that project; existing `doc/` files are preserved (the
  scaffolder skips files that already exist).

---

## [3.4.0]: 2026-03-30

### Added
- **Version Control Discipline** added to Non-Negotiable Standards in `CLAUDE.md` and `GEMINI.md`.
  Mandates branch-based workflow, bans direct pushes to `main`, and requires `doc/version_control.md`
  to be read before any git operation. Applies to all team members including AI agents.
- Protocol version bumped to 2.4.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you re-initialize an existing project session, the version control discipline rules will apply.

---

## [3.3.0]: 2026-03-27

### Changed
- Recommended consumption pattern is now **gitignored local clone**: clone the toolkit into
  your project root and add `organisation/` to `.gitignore`. The toolkit stays local and
  updatable but is never committed to the consuming project.
- Step 4 of the Initialize Protocol updated to show the simpler `--output-dir .` form
  (works when toolkit is gitignored inside the project root). Protocol version bumped to 2.2.

### Removed
- Static copy pattern (Pattern B) removed from documentation, strictly inferior to gitignored clone.

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you had `organisation/` tracked as files in a consuming project, remove it:
  `git rm -r organisation/ && echo "organisation/" >> .gitignore`
  then re-clone: `git clone https://github.com/Number-Pii/organisation.git organisation`

---

## [3.2.0]: 2026-03-27

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

## [3.1.0]: 2026-03-26

### Added
- **Step 6 (Scope Discipline)** added to the Initialize Protocol in CLAUDE.md and GEMINI.md.
  Enforces `doc/project-brief.md` as the hard boundary for all project work. Existing projects
  are unaffected; this only applies when starting new tasks or new AI sessions.
- **Mandatory Handover Rule** added to Step 7. Clarifies that no task is complete until handover
  notes are updated. No changes to the `doc/` file structure; existing handover files are compatible.

### Changed
- Welcome message corrected: "Welcome to Number Pii" (was "Welcome, Number Pii").

### Migration Notes
- No action required for existing projects. Your `doc/` folder is unchanged.
- If you re-initialize an existing project session, the stricter scope and handover rules will apply.

---

## [3.0.0]: 2026-03-25

### Added
- Full skill linking across all 53 role files: Core Skills, Technical Skills, and Agent Skills layers.
- `Teams/skills/` directory with 1,294 AI skill modules.
- `scripts/audit_skills.py`: skill coverage auditor.
- `GEMINI.md`: Gemini CLI counterpart to CLAUDE.md (identical content).
- `scripts/README.md`: script usage documentation.

### Changed
- Initialize Protocol expanded from 5 steps to 7 steps (added Step 6 and Step 7).
- `scripts/init_project.py` updated with richer templates including Decision Authority Matrix
  and Completion Criteria sections.

### Migration Notes
- **MAJOR version**: If upgrading from 2.x, the Initialize Protocol has new steps.
- Existing `doc/` files created with 2.x templates remain valid; no reformatting needed.
- New projects will get the richer 3.x templates automatically.

---

## [2.0.0]: 2026-02-01

### Added
- Initial `scripts/init_project.py` scaffolder.
- `doc/` folder structure: project-brief, team-assignment, workflow, version_control, handover.
- Consolidated handover and department handover note templates.

---

## [1.0.0]: 2025-12-01

### Added
- Initial organisation structure: 53 roles across 6 departments.
- `Teams/organisation.md`: master org chart, delegation model, approval authority matrix.
- `CLAUDE.md` with Initialize Protocol (Steps 1-5).
