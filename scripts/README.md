# Number Pii: Scripts

Python 3 scripts that automate deterministic work, saving tokens and time.

---

## `check_writing.py`: Writing Standard Validator

Checks prose deliverables (markdown or plain text) against `WRITING.md`. The banned-phrases
list is read live from `WRITING.md`, so the standard has a single source of truth.

### Usage
```bash
# Professional/technical prose (default Flesch target 30-40)
python3 scripts/check_writing.py doc/project-brief.md

# Marketing copy (higher readability target)
python3 scripts/check_writing.py landing-copy.md --target-min 50 --target-max 65

# Treat warnings as failures (editorial gate / CI use)
python3 scripts/check_writing.py report.md --strict
```

### What It Checks
| Severity | Check |
|----------|-------|
| FAIL | Em dashes (—) and en dashes (–), with line numbers |
| FAIL | Banned phrases from `WRITING.md`, with line numbers |
| FAIL | Three or more consecutive sentences with the same opener |
| WARN | Flesch Reading Ease outside the target band |
| WARN | Low sentence-length variety; dominant sentence opener |
| WARN | Passive voice above ~30% of sentences (approximate) |

Exit code 0 on pass, 1 on any FAIL (or WARN with `--strict`). Code blocks, inline code,
and HTML comments are excluded from scanning.

---

## `audit_skills.py`: Skill Coverage Auditor

Reports how well each role file's Core Skills and Technical Skills are linked to `@skill-name`
references from `Teams/skills/`.

### Usage
```bash
# Run from repo root
python3 scripts/audit_skills.py

# Plain output (no ANSI colour, good for Gemini CLI or CI)
python3 scripts/audit_skills.py --no-color

# Also write an audit_report.md file to scripts/
python3 scripts/audit_skills.py --report

# Rewrite stale size_class values to match actual line counts
python3 scripts/audit_skills.py --fix
```

> `scripts/audit_report.md` is generated output. It is gitignored and must not be
> committed; regenerate it locally with `--report` whenever you need a fresh copy.

The audit exits non-zero on broken `@skill` refs or frontmatter drift, so CI
gates on it. It also reports skill tier counts and lists curated skills whose
`risk` field is still `unknown` (reported, not failing).

### What It Reports
| Metric | Description |
|

---

## `find_skill.py`: Skill Search

Searches `Teams/skills/skills-index.json` by keyword without loading any SKILL.md.
Reviewed skills show by default; `--all` adds the rest, `--domain` narrows.

```bash
python3 scripts/find_skill.py postgres
python3 scripts/find_skill.py --domain "Testing & QA" --all e2e
```

---

## `build_skills_index.py`: Skills Index Generator

Generates `Teams/skills/skills-index.json` (consumed by `find_skill.py`) and
`Teams/skills/CATEGORIES.md` from each skill's frontmatter. Both outputs are
generated files: edit frontmatter, regenerate, commit all three together.

### Usage
```bash
# Rewrite both generated files
python3 scripts/build_skills_index.py

# CI mode: exit 1 if either file is stale
python3 scripts/build_skills_index.py --check
```

--------|-------------|
| Total skill folders | How many skills exist in `Teams/skills/` |
| Agent Skills refs | Unique `@skill` refs across all 53 Agent Skills sections |
| Broken refs | `@skill` refs that have no matching folder |
| Bullet coverage | Core/Technical bullets WITH and WITHOUT inline `@skill` refs |
| Unlinked skills | Skills in `Teams/skills/` not referenced in any role file |
| Per-role summary | ✓ / ~ / ✗ coverage status per role |

---

## `init_project.py`: Project Scaffolder

Creates the standard scaffold in a consuming project. Run it once the brief,
level, and team are agreed; it never overwrites an existing file.

Content comes from `templates/` at the toolkit root, rendered with Python's
`string.Template`; wording changes are markdown edits, not code edits. The
classification level sets the quality gates and writes level-matched Pull Request
Rules and Release Process sections into `version_control.md`. Template changes must
regenerate the golden files; see `tests/README.md`.

### Usage
```bash
python3 organisation/scripts/init_project.py \
  --project-name "API Build" --level 2 --output-dir /path/to/my-project

# Existing product (brownfield), preview only
python3 organisation/scripts/init_project.py \
  --project-name "Inherited App" --level 3 --existing --output-dir . --dry-run
```

### Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--project-name` | (required) | Project name used in file headers |
| `--output-dir` | `.` (current dir) | The consuming project root; refused if it is the toolkit itself |
| `--level` | `2` | Classification level 1-4; sets the quality gates. Level 3+ adds `architecture.md` |
| `--existing` | false | Brownfield mode; adds `codebase-assessment.md` and existing-product context in `STATE.md` |
| `--no-claude-hooks` | false | Skip the `.claude/` hook; the git `pre-push` hook is always written |
| `--departments` | `engineering` | Accepted for compatibility; handover is per branch since 4.0.0 |
| `--dry-run` | false | Preview the structure without creating files |

### What It Creates
```
AGENTS.md                     # Project description + the toolkit's managed block
CLAUDE.md, GEMINI.md          # Stubs importing AGENTS.md
.githooks/pre-push            # Refuses pushes to main (git config core.hooksPath .githooks)
.claude/                      # Optional Claude Code guard hook
doc/
├── README.md                 # The doc map: what each file and folder is for
├── project-brief.md          # Goals, scope, constraints, classification level
├── team-assignment.md        # Roles and responsibilities
├── workflow.md               # Planned task chain + level quality gates
├── version_control.md        # Branching, PR rules, parallel work, releases
├── task-board.md             # Board config + backlog for gh_project_sync.py
├── architecture.md           # Level 3 and 4 only
├── codebase-assessment.md    # Brownfield only
└── handover/
    ├── STATE.md              # Consolidated state; changes only in consolidation PRs
    └── entries/              # One file per branch, edited only by that branch
```

---

## `handover.py`: Per-Branch Handover

Each branch keeps one entry in `doc/handover/entries/`; `STATE.md` changes only in
`chore/handover-consolidate-*` PRs. Parallel branches never edit the same lines.

```bash
python3 organisation/scripts/handover.py new --issue 12     # this branch's entry, pre-filled from commits
python3 organisation/scripts/handover.py status             # in flight and not yet consolidated
python3 organisation/scripts/handover.py check              # fails if a PR edits another branch's entry
python3 organisation/scripts/handover.py consolidate        # draft for STATE.md; --mark records the date
```

---

## `docs.py`: Documentation Map and Check

`map` prints every document under `doc/` with a one-line summary. `check` fails when
a top-level file or an unknown folder is missing from `doc/README.md`, or when a
relative link is broken. Files inside mapped folders need no index edit. Run on the
toolkit itself, it checks that every root document is referenced from `AGENTS.md` or
`README.md`.

---

## `sync_context.py`: Managed Block Sync

Replaces the `<!-- np:begin -->` ... `<!-- np:end -->` block in a project's `AGENTS.md`
with the current `templates/agents-block.md`, touching nothing else and writing only
when the bytes differ. `--check` reports staleness. A file without the block is
refused; `--append` adds it to the end of a hand-written file.

---

## `migrate_consumer.py`: Move a Pre-4.0 Project to v4

Opt-in. From a consuming project root it prints what it would change; `--apply`
makes the changes, and it never commits. It turns `consolidated_handover.md` into
`STATE.md`, adds the entries folder and a `doc/README.md` map listing existing
documents, replaces toolkit-generated context pointers with `AGENTS.md` and stubs,
and updates the hooks. Hand-written context files are never touched.

```bash
python3 organisation/scripts/migrate_consumer.py            # dry run
python3 organisation/scripts/migrate_consumer.py --apply
```

---

## `gh_project_sync.py`: GitHub Project Orchestration Bridge

Connects a project's planned backlog to a live GitHub Project board. The toolkit plans the
work; GitHub Projects runs it. Rules for that handoff, the six workflow states, and the
ownership-locking convention live in `GITHUB_ORCHESTRATION.md` at the toolkit root.

The script reads `doc/task-board.md` (scaffolded by `init_project.py`), creates issues, applies
the standard labels, adds items to the project, and queries the board so any contributor reads
current ownership before claiming work.

### Prerequisites
- GitHub CLI installed and authenticated: `gh auth login` (confirm with `gh auth status`)
- `doc/task-board.md` present, with the Board Configuration table filled in (project number,
  project owner, repository)

### Usage
```bash
# See who owns what before claiming anything (the awareness step)
python3 organisation/scripts/gh_project_sync.py query

# Preview the gh calls, then push the backlog to the board
python3 organisation/scripts/gh_project_sync.py push --dry-run
python3 organisation/scripts/gh_project_sync.py push

# Claim a task: assign an owner and move its workflow state
python3 organisation/scripts/gh_project_sync.py assign --issue 42 \
  --assignee your-handle --state "In Progress"

# Set the board Status field directly, or pull live state back into the doc file
python3 organisation/scripts/gh_project_sync.py status --issue 42 --state Review
python3 organisation/scripts/gh_project_sync.py sync

# Record a blocked-by dependency between two issues
python3 organisation/scripts/gh_project_sync.py link --issue 42 --blocked-by 40
```

### Subcommands
| Command | What it does |
|---------|--------------|
| `push` | Create issues from `doc/task-board.md`, label them, and add them to the project (idempotent: skips titles already on the board) |
| `assign` | Set or clear an issue's owner and move its workflow state; sets the board Status field automatically. Refuses to take over a claimed item (assigned + In Progress) without `--force` |
| `status` | Set the project board Status field for one issue (discovers the field and option IDs itself) |
| `sync` | Report where `doc/task-board.md` differs from the live board; `--write-back` snapshots the board into the file |
| `query` | List open items with board status, owner, and blocking issues; add `--json` for structured output |
| `link` | Record a blocked-by dependency between two issues |

Every subcommand accepts `--dry-run`, which prints the `gh` calls without running them. The flag
works in either position, before or after the subcommand (`--dry-run push` and `push --dry-run`
are equivalent). When a precondition is missing (no `gh`, not authenticated, or unset
configuration), the script stops with a clear message rather than guessing.

---

## `build_org.py` and `build_agents.py`: Org Structure as Data

`build_org.py` generates `Teams/org.json` from the role files: departments,
reporting lines, approval authority, and agent skills as machine-readable data.
`build_agents.py` generates Claude Code subagent definitions in `agents/` for
the core delivery roles listed in its `CORE_ROLES` table. Role markdown stays
the source of truth; both outputs are generated, CI fails on drift, and both
scripts take `--check`.

```bash
python3 scripts/build_org.py && python3 scripts/build_agents.py
```

---

## `run_evals.py`: Skill Eval Runner

Runs the golden tasks in `evals/tasks/` twice each (bare, and with the skill
under test loaded) and writes side-by-side results for rubric judging. Needs
the `claude` CLI for live runs; `--list` works without it. Method and task
format: `evals/README.md`.

---

## `update.py`: Toolkit Updater

Moves this toolkit clone forward to the latest release tag.
**Your project `doc/` files are never affected**; they live in your own project repo, not here.

### Usage
```bash
# Check if an update is available (no changes made)
python3 scripts/update.py --check

# Check and prompt to install
python3 scripts/update.py

# Update without prompting
python3 scripts/update.py --yes

# Track the tip of main instead of release tags
python3 scripts/update.py --follow-main

# Show full changelog
python3 scripts/update.py --changelog
```

### What It Does
1. Runs `git fetch --tags` and finds the highest `vX.Y.Z` tag
2. Leaves the clone alone if it is already on or ahead of that release
3. Warns if a **MAJOR** version bump requires reading migration notes
4. Checks out the release tag (detached HEAD) if confirmed

`main` can hold merged work that has not been released yet (changelog
fragments waiting for a release PR), which is why clones follow tags.

### Pinning a version
A `.toolkit-pin` file containing a git ref (usually a release tag such as
`v3.15.0`) pins the clone to that ref. Put it in the consuming project root,
next to the `organisation/` clone; a pin inside the clone works as a fallback.
While pinned, `update.py` checks out the pinned ref instead of following
releases; delete the file and run `update.py` again to resume normal updates.

### Version Types
| Bump | Meaning | Safe to update? |
|------|---------|----------------|
| PATCH (3.1.x) | Wording fixes, skill additions | Always safe |
| MINOR (3.x.0) | New steps or features in the protocol | Safe; read changelog |
| MAJOR (x.0.0) | Initialize Protocol restructured | Read migration notes first |

---

## `update_all.py`: Fan-Out Updater

Updates every consuming project's clone listed in `consumers.json` (toolkit
root) and prints a version matrix. Each clone updates through its own
`update.py`, so per-consumer pins are respected and no `doc/` file is touched.

### Usage
```bash
# Version matrix only, change nothing
python3 scripts/update_all.py --check

# Update every registered clone
python3 scripts/update_all.py
```

Register or remove a consumer by editing `consumers.json`; entries are a name
plus a path relative to the registry's `base`.

---

## `check_plugin.py`: Plugin Packaging Check

Validates the Claude Code plugin surface: `plugin.json` and `hooks.json` parse,
referenced hook scripts exist, `commands/init.md` and `agents/` are present, and the
plugin and scaffold copies of the main-branch hook are byte-identical.

---

## `release.py`: Release Builder

Compiles the changelog fragments in `changes/` into a new `CHANGELOG.md`
section, bumps `VERSION` and `.claude-plugin/plugin.json` by the highest `bump`
any fragment declares, and deletes the fragments. Run it on a
`chore/release-X.Y.Z` branch; see [changes/README.md](../changes/README.md).

```bash
python3 scripts/release.py --dry-run         # preview
python3 scripts/release.py                   # write the release
python3 scripts/release.py --version 4.0.0   # force a version
```

---

## `check_version.py`: Version Sync Check

Fails if `VERSION`, the latest `CHANGELOG.md` heading, and the plugin manifest
disagree. With `--require-fragment <base>` (CI on every PR) it also fails when
the diff against `<base>` adds no `changes/` fragment and is not a release.

---

## Requirements
- Python 3.9+ (no external dependencies)
- Run from the repo root or provide the full path to the script
- `update.py` requires the repo to have been cloned via git (not downloaded as a ZIP)
