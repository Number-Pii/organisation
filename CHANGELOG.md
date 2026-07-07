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

## [3.19.0]: 2026-07-07

### Added
- **Claude Code plugin packaging.** The repo doubles as an installable plugin
  (`.claude-plugin/plugin.json`): the Initialize Protocol becomes `/np:init`
  (it cannot be run from memory), the main-branch protection hook applies
  wherever the plugin is enabled, and the core role agents install natively.
  The manifest version is pinned to `VERSION` by `check_version.py`, and a
  test pins the plugin hook byte-identical to the scaffold template.
- **Roles as agents.** `scripts/build_agents.py` generates Claude Code
  subagent definitions in `agents/` for five core delivery roles (backend
  lead, frontend lead, senior PM, QA automation, information security), each
  carrying the delegated-authority governance note and its approval
  boundaries. Generated from role markdown; CI fails on drift.
- **Org structure as data.** `scripts/build_org.py` generates `Teams/org.json`
  (6 departments, 53 roles, reporting lines, approval authority, agent
  skills); `audit_skills.py` now reads its department list from it instead of
  a hardcoded constant. CI fails on drift.
- **Skill evals v1.** `evals/` defines nine golden tasks across
  backend, frontend, and writing, each with a scoring rubric;
  `scripts/run_evals.py` runs every task bare and with the skill under test
  and stores side-by-side results for rubric judging. Curation becomes
  evidence-driven; tier changes still need a human sign-off.
- **Knowledge loop.** `scripts/draft_handover.py` drafts dated handover
  entries from git history (grouped by commit type, `--write` to append);
  `templates/learnings.md` plus a new closure checklist item make a one-page
  learnings file part of every project's exit.

### Pending
- The first `products/` pack still needs durable product facts from the
  founders; the spec and template are ready.

---

## [3.18.0]: 2026-07-07

### Added
- **`gh_project_sync.py` sets the board Status field itself.** `assign --state`
  now updates the GitHub Project Status column via the Projects v2 API
  (field and option IDs discovered per project), replacing the v1 instruction
  to set it by hand. A new `status` subcommand moves one issue's Status
  directly. Verified read-side against the live CalyPad board.
- **The ownership lock is enforced.** `assign` refuses to reassign an item
  that is assigned and In Progress unless `--force` is passed, closing the gap
  where a second contributor could silently take over claimed work.
- **`sync` writes the board back into the doc file.** Live Status values
  rewrite the State column of `doc/task-board.md` (template comment rows and
  other sections untouched), closing the acknowledged one-directional gap in
  the orchestration layer.

### Changed
- `GITHUB_ORCHESTRATION.md` now describes the two-way flow and the enforced
  claim rule; `scripts/README.md` and the `@github-project-orchestrator` skill
  document the new subcommands.

---

## [3.17.0]: 2026-07-06

### Added
- **Enforcement as code in every scaffold.** `init_project.py` now writes a
  `.claude/` folder into consuming projects: a PreToolUse hook that blocks git
  commits and pushes on `main` or `master` (exit 2 with the version-control
  rule quoted back), and a SessionStart hook that injects the context-file
  checklist. The standards stop being prose-only for Claude Code sessions; the
  markdown contract remains the rule for Gemini CLI and Codex. Existing
  `.claude/settings.json` files are never overwritten.
- **Version pinning via `.toolkit-pin`.** A file containing a git ref (usually
  a release tag) in the consuming project root, or in the clone, holds the
  toolkit at that ref; `update.py` checks out the pin instead of following
  `main`, and returns cleanly to `main` when the pin is removed.
- **Consumer registry and fan-out updater.** `consumers.json` at the toolkit
  root records the eleven consuming projects; `scripts/update_all.py` updates
  every registered clone through its own `update.py` (pins respected) and
  prints a before/after version matrix. `--check` reports the matrix without
  changing anything.

### Changed
- `update.py` fetches tags and recovers from a detached HEAD left by an
  earlier pin before fast-forwarding.
- `INITIALIZE.md` Step 4 documents the scaffolded `.claude/` enforcement
  layer; `README.md` and `scripts/README.md` document pinning and the fan-out
  updater.

---

## [3.16.0]: 2026-07-06

### Added
- **Skill tiers.** Every skill now carries a tier in frontmatter: `curated`
  (reviewed and role-referenced, 195 skills), `standard` (unreviewed community
  content, the default), or `archive` (off-charter, 30 skills: celebrity
  personas, Portuguese legal skills, health analyzers, and two demo-payload
  skills). The tier is the supply-chain review gate; `CONTRIBUTING.md` gains a
  promotion checklist and demotion rule.
- **Canonical markers.** `canonical: true` marks the preferred skill in five
  duplicate clusters (postgresql, software-architecture, domain-driven-design,
  test-driven-development, systematic-debugging); canonicals sort first in
  search and in CATEGORIES.md.
- **`scripts/build_skills_index.py`.** Generates `Teams/skills/skills-index.json`
  and regenerates `CATEGORIES.md` from skill frontmatter; CI fails when either
  drifts. CATEGORIES.md is now generated output with its domain descriptions
  carried over between generations.
- **`audit_skills.py --fix`** rewrites stale `size_class` values (117 fixed in
  this release). The audit also reports tier counts and curated skills whose
  `risk` is unreviewed.

### Changed
- **`find_skill.py` searches summaries and gates by tier.** Matching covers
  names and frontmatter summaries; only curated skills surface by default, with
  a hidden-match count pointing at `--all` and `--tier`. Canonicals rank first.
  Results read from `skills-index.json` with a live-scan fallback.
- **The skill audit now fails CI on drift.** It previously always exited zero,
  so the "fails on broken refs" gate was inert; broken refs and frontmatter
  issues now exit non-zero. Five over-length summaries this exposed were
  trimmed.
- **Protocol version 2.15.** The Skills section of `CLAUDE.md` documents tiers,
  canonical preference, and the risk check; `GEMINI.md` and `AGENTS.md`
  regenerated.

### Removed
- **22MB of non-functional binary payloads**: `last30days/assets` (14MB of demo
  media) and `loki-mode` benchmarks and demo gif (8.8MB). Both skills are now
  archive-tier; the library drops from 63MB to 41MB.

---

## [3.15.0]: 2026-07-06

### Added
- **Pytest suite for the load-bearing scripts** (`tests/`, run in CI). Golden-file
  tests pin scaffold output byte for byte at every classification level and in
  brownfield mode; fixture tests cover the frontmatter and task-board parsers,
  including malformed input; unit tests cover `check_writing.py` and
  `check_version.py`. `tests/generate_goldens.py` regenerates the goldens after
  an intentional template change, and the diff is reviewed in the PR.
- **CI validates rendered scaffolds against the Writing Standard.** A new step
  renders a full Level 4 brownfield scaffold and runs `check_writing.py` over
  every generated file, closing the gap where scaffolded docs landed in
  consuming repos unchecked.

### Changed
- **Scaffold templates extracted from code to `templates/*.md`.** All eleven doc
  templates that lived as inline f-strings in `init_project.py` are now markdown
  files rendered with stdlib `string.Template`. Wording changes are markdown
  edits; the script keeps only structure and the `LEVELS` table. The script
  shrinks from 808 lines to roughly 280.
- **`version_control.md` scaffolds are level-enforcing, not level-aware.** The
  Pull Request Rules and Release Process sections now render from the `LEVELS`
  table: Level 4 writes two approving reviews, CTO-level sign-off, and signed
  releases into the contract, where every level previously got the same
  "at least 1 peer review" line.
- **Shared parser moved to `scripts/lib/`.** The frontmatter parser that
  `find_skill.py` and `generate_skill_frontmatter.py` imported from
  `audit_skills.py` via `sys.path` insertion now lives in
  `scripts/lib/frontmatter.py`; `audit_skills.py` re-exports it so existing
  import paths keep working.

---

## [3.14.2]: 2026-07-06

### Added
- **CI tags releases automatically.** A new `tag-release` job runs on every push
  to `main` after validation passes; it creates and pushes the annotated
  `v$(cat VERSION)` tag when it is missing. Releases v3.14.0 and v3.14.1 shipped
  untagged, and this closes that gap for good. The manual tagging command in
  `CONTRIBUTING.md` remains as a fallback.

### Fixed
- **`check_version.py` now covers `AGENTS.md`.** The protocol-version check
  compared `CLAUDE.md` against `GEMINI.md` only, so a stale `_Version` line in
  `AGENTS.md` would have passed CI unnoticed. All generated context files are now
  checked against `CLAUDE.md`.
- **`scripts/audit_report.md` is no longer tracked.** The file is generated output
  from `audit_skills.py --report`; it is removed from version control and
  gitignored, with a note in `scripts/README.md`.

### Changed
- **`Teams/_role_template.md` matches audit behaviour on Technical Skills.** The
  template claimed all three skill sections were mandatory, yet nine sales and
  executive roles omit Technical Skills and the audit accepts them. The template
  now states that Technical Skills is required for technical roles and optional
  where a role has no tool-specific competencies.

---

## [3.14.1]: 2026-06-24

### Fixed
- **`gh_project_sync.py` accepts `--dry-run` in either position.** The flag was a
  global option only, so placing it after the subcommand (`push --dry-run`) failed
  with an "unrecognized arguments" error, which is the order the docs themselves
  showed. Each subcommand now also accepts `--dry-run`, so `--dry-run push` and
  `push --dry-run` are equivalent.
- **Docs match the working behaviour.** `scripts/README.md` and the
  `github-project-orchestrator` skill now state that `--dry-run` works before or
  after the subcommand.

---

## [3.14.0]: 2026-06-23

### Added
- **GitHub Project Orchestration Layer (foundational v1).** The toolkit now plans
  the work and a GitHub Project board runs it. New binding spec
  `GITHUB_ORCHESTRATION.md` at the root defines six standard workflow states
  (Backlog, Ready, In Progress, Review, Blocked, Completed), a label taxonomy, the
  owner registry (human roles and virtual agents), and a GitHub-native
  ownership-locking convention: a task is claimed once it has an assignee and sits
  in In Progress, so the board is the single source of truth and no separate ledger
  drifts.
- **`scripts/gh_project_sync.py`:** a deterministic `gh` CLI wrapper with `push`,
  `assign`, `query`, and `link` subcommands, each supporting `--dry-run`. It reads a
  project's backlog from `doc/task-board.md`, creates labelled issues, adds them to
  the project, and reports board ownership so contributors query before claiming.
- **`@github-project-orchestrator` skill** (Planning & Workflow): the agentic loop
  for decomposing epics, matching owners, and claiming work without collision. It
  cross-links `@create-issue-gate`, `@github-issue-creator`, and
  `@acceptance-orchestrator`.
- **`doc/task-board.md` scaffold:** `init_project.py` now creates a task board in
  every project, holding the board configuration and the backlog decomposed from
  `workflow.md`.

### Changed
- `INITIALIZE.md` gains Step 5b (set up the execution board) under the Planning
  stage, with an awareness-first rule before any implementation task.
- `CLAUDE.md` adds a GitHub Project Orchestration pointer; protocol version bumped
  to 2.14. `GEMINI.md` and `AGENTS.md` regenerated.

## [3.13.4]: 2026-06-10

### Changed
- **Founders' pronouns recorded.** Both co-founders use he/him: Olatunbosun
  Iyare (he/him) and Destiny Ihejirika (he/him). Stated in the Governance
  sections of `CLAUDE.md` and `Teams/organisation.md` and in `README.md`, with
  a binding instruction to use these pronouns in every document that refers to
  either founder. Prevents misgendering in official project documents and
  client-facing material.
- `GEMINI.md` and `AGENTS.md` regenerated.

## [3.13.3]: 2026-06-10

### Changed
- **Skills curation, final slice: frontmatter coverage complete.** Extended
  frontmatter backfilled for the remaining 1,094 skills; coverage is now
  1,290/1,294 (the four exceptions are container directories without a
  SKILL.md: `docs/`, `libreoffice/`, `linear/`, `security/`, plus `SPDD`,
  which ships staged files instead).
- **Summary quality pass over the whole library:** 55 persona-opener summaries
  rewritten mechanically; 33 degenerate summaries (YAML block-scalar markers
  captured as text) rederived from their description blocks, 22 of those
  finished by hand.
- **57 misclassifications corrected** after a prefix-family consistency scan,
  in both `CATEGORIES.md` and skill frontmatter: the Makepad family
  consolidated under Frontend & UI, the n8n family under SaaS Integrations,
  the fp-* references under Programming Languages, plus assorted single fixes
  (judicial-auction skills out of Mobile, `create-branch` out of Creative &
  Design, and similar).
- Catalogue and frontmatter now agree on the domain of every skill in the
  library: zero mismatches.

## [3.13.2]: 2026-06-10

### Changed
- **Skills curation, slice two: the catalogue is complete.** All 571 remaining
  uncategorised skills are now placed in `CATEGORIES.md`, so every one of the
  1,294 skills resolves a domain through `find_skill.py --domain`:
  - 508 classified by an ordered keyword ruleset over names and frontmatter
    descriptions; 63 stragglers assigned by hand after reading their descriptions.
  - The Azure SDKs section previously described its ~116 skills by prefix only,
    which tooling could not read (azure skills returned `uncategorised`); it now
    carries an explicit list like every other section.
  - Skill-token regexes in `find_skill.py` and `generate_skill_frontmatter.py`
    widened to accept uppercase and underscores (`SPDD`,
    `android_ui_verification`), the only two names the old pattern missed.
- No new domains were needed; the 18 existing domains absorbed everything.
  Frontmatter backfill for unlinked skills remains deliberately deferred; domain
  resolution works from the catalogue without it.

## [3.13.1]: 2026-06-10

### Changed
- **Skills curation, slice one (audit recommendation 1).** The role-linked portion
  of the library is now fully curated:
  - 51 role-linked skills added to `CATEGORIES.md`: 35 placed across ten existing
    domains, 16 in the new **Business & Strategy** domain (business analysis,
    startup strategy, finance, sales, HR, people operations).
  - Extended frontmatter backfilled for 180 role-linked skills via
    `generate_skill_frontmatter.py --write`; coverage rises from 16/1294 (1%)
    to 196/1294 (15%). Every role-linked skill now resolves a real domain;
    zero `uncategorised` among them.
  - 20 generated summaries that started as persona openers ("You are an
    expert...") rewritten as one-line "what's this skill for" statements per
    the CONTRIBUTING guidance.
- Remaining uncategorised refs are the four placeholders in `_role_template.md`,
  which are intentional. The unlinked 1,099 skills stay discoverable through
  `find_skill.py` and are the next curation slice.

## [3.13.0]: 2026-06-10

### Added
- **Audit remediation release.** Implements the High, Medium, and tag-related Low
  priority recommendations from the formal toolkit audit:
  - **CI writing enforcement:** the Toolkit CI workflow now compiles
    `check_writing.py` and `check_handover.py` and validates every maintained
    markdown file against the Writing Standard on each PR.
  - **Pre-commit hook shipped:** `.githooks/pre-commit` runs the version check,
    adapter sync check, and writing validator on staged markdown. Install with
    `git config core.hooksPath .githooks` (documented in CONTRIBUTING).
  - **`scripts/check_handover.py`:** staleness checker for consuming projects;
    fails when the consolidated handover is more than N commits behind the work.
  - **Adjacent-role boundaries:** new "Choosing Between Adjacent Roles" table in
    `Teams/organisation.md` covering the eight closest role pairs.
  - **Product context packs:** new `products/` registry (README plus template).
    One pack per product, loaded only when working on that product; Product
    Neutrality applies inside packs. `CLAUDE.md` gains a compact Products section.
  - **Level 1 fast path** in `INITIALIZE.md`: confirmed Level 1 projects may
    compress Steps 3 to 5; Steps 6 to 8 still apply in full.
  - **Concurrent-sessions convention** in the scaffolded `version_control.md`:
    one session per branch, append-only handover notes, single consolidator.
  - **Release tagging** documented in CONTRIBUTING; releases are tagged from
    this version onward (current main retro-tagged `v3.12.2`).

### Changed
- Protocol version bumped to 2.13 in `CLAUDE.md`; `GEMINI.md` and `AGENTS.md`
  regenerated.

## [3.12.2]: 2026-06-10

### Changed
- **Banned-phrase sweep.** Toolkit prose now passes its own validator end to end:
  all 65 maintained markdown files clear `check_writing.py` with zero failures.
  Five banned phrases rewritten in role files and `philosophy.md` (`robust`,
  `empower`, and three `world-class` uses, now "reliable", "develop", "elite",
  "exceptional", and "top 1% of their field").
- Two repeated-opener runs broken up: the README audience guide no longer starts
  four consecutive paragraphs with "For", and CHANGELOG PR citations are varied
  so reference lists do not trip the consecutive-opener check.
- `check_writing.py` now exempts rule statements that name the dash characters,
  e.g. "no em dashes (—)", so the standard's own text does not flag itself.
  Regression-tested: real dashes on the same line still fail.

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
  extension fields from an existing SKILL.md and supports in-place `--write`. (also in PR #6)
- **`scripts/audit_skills.py`** extended with a zero-dep YAML subset parser, an
  opt-in validator for the four extension fields, and a new coverage stat
  (`Skills with extended frontmatter: N/1294`). (same PR)
- **16 pilot skills** extended with the new frontmatter: `project-development`,
  `internal-comms`, `analytics-product`, `api-design-principles`,
  `writing-plans`, `security-audit`, `aws-skills`,
  `javascript-testing-patterns`, `react-best-practices`, `workflow-automation`,
  `postgresql`, `cloud-architect`, `backend-dev-guidelines`,
  `software-architecture`, `e2e-testing`, `fp-refactor`. (completed in PR #6)
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
