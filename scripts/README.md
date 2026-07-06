# Number Pii: Scripts

Python 3 scripts that automate deterministic work, saving tokens and time.

---

## `check_handover.py`: Handover Staleness Checker

Flags a consolidated handover that has fallen behind the work it describes, by
counting commits since the handover file was last touched.

### Usage
```bash
# From a consuming project root (default limit: 20 commits)
python3 organisation/scripts/check_handover.py

# Stricter limit
python3 organisation/scripts/check_handover.py --max-commits 10
```

Exit code 0 when fresh; 1 when the handover is stale, missing, or never committed.

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

### What It Reports
| Metric | Description |
|--------|-------------|
| Total skill folders | How many skills exist in `Teams/skills/` |
| Agent Skills refs | Unique `@skill` refs across all 53 Agent Skills sections |
| Broken refs | `@skill` refs that have no matching folder |
| Bullet coverage | Core/Technical bullets WITH and WITHOUT inline `@skill` refs |
| Unlinked skills | Skills in `Teams/skills/` not referenced in any role file |
| Per-role summary | ✓ / ~ / ✗ coverage status per role |

---

## `init_project.py`: Project Scaffolder

Creates the standard `doc/` folder structure in any project directory. Run after your AI
coding assistant has determined the project brief and team assignment.

Content comes from `templates/*.md` at the toolkit root, rendered with Python's
`string.Template`; wording changes are markdown edits, not code edits. The
classification level sets the quality gates, and it also writes level-matched
Pull Request Rules and Release Process sections into `version_control.md`
(Level 4 scaffolds two reviewers and CTO sign-off, not a generic one-review rule).
Template changes must regenerate the golden files; see `tests/README.md`.

### Usage
```bash
# Basic: creates doc/ in the current directory
python3 /path/to/org/scripts/init_project.py --project-name "My Project"

# With specific departments (creates dept handover sub-folders)
python3 /path/to/org/scripts/init_project.py \
  --project-name "Client Landing Page" \
  --departments "engineering,design,marketing"

# Into a specific project directory, with a classification level
python3 /path/to/org/scripts/init_project.py \
  --project-name "API Build" \
  --departments "engineering" \
  --output-dir /path/to/my-project \
  --level 2

# Preview without creating files
python3 /path/to/org/scripts/init_project.py \
  --project-name "Test" \
  --dry-run
```

### Arguments
| Argument | Default | Description |
|----------|---------|-------------|
| `--project-name` | (required) | Project name used in all file headers |
| `--departments` | `engineering` | Comma-separated dept names for handover sub-folders |
| `--output-dir` | `.` (current dir) | Directory where `doc/` will be created |
| `--level` | `2` | Classification level 1-4; sets the quality gates written into the docs. Level 3+ adds `architecture.md` |
| `--existing` | false | Brownfield mode; adds `codebase-assessment.md` and expands the handover template |
| `--dry-run` | false | Preview the structure without creating files |

### What It Creates
```
doc/
├── project-brief.md          # Goals, scope, client, constraints, classification level
├── team-assignment.md        # Assigned team members and their responsibilities
├── workflow.md               # Step-by-step task chain + level quality gates
├── version_control.md        # Git strategy, branching, PR rules
├── task-board.md             # Execution board config + backlog for gh_project_sync.py
├── architecture.md           # System design (created at --level 3 and 4 only)
└── handover/
    ├── consolidated_handover.md   # Current project state (always up to date)
    └── [dept-name]/               # One folder per department in the team
        └── handover-notes.md      # Dept-specific notes, updated as work progresses
```

### Handover Workflow
The `doc/handover/` system saves tokens and time when switching AI sessions:

1. **During work**: Each team member updates their dept `handover-notes.md`
2. **At milestones**: Team lead pulls from dept notes → updates `consolidated_handover.md`
3. **New session**: Tell the AI: *"Initialize CLAUDE.md and read doc/handover/consolidated_handover.md"*
4. The new session has full context immediately, no re-explanation needed

---

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

# Record a blocked-by dependency between two issues
python3 organisation/scripts/gh_project_sync.py link --issue 42 --blocked-by 40
```

### Subcommands
| Command | What it does |
|---------|--------------|
| `push` | Create issues from `doc/task-board.md`, label them, and add them to the project (idempotent: skips titles already on the board) |
| `assign` | Set or clear an issue's owner and move its workflow state (the claim/lock operation) |
| `query` | List open board items with owner, state, and labels; add `--json` for raw output |
| `link` | Record a blocked-by dependency between two issues |

Every subcommand accepts `--dry-run`, which prints the `gh` calls without running them. The flag
works in either position, before or after the subcommand (`--dry-run push` and `push --dry-run`
are equivalent). When a precondition is missing (no `gh`, not authenticated, or unset
configuration), the script stops with a clear message rather than guessing.

---

## `update.py`: Toolkit Updater

Checks for updates to this toolkit and pulls the latest version safely.
**Your project `doc/` files are never affected**; they live in your own project repo, not here.

### Usage
```bash
# Check if an update is available (no changes made)
python3 scripts/update.py --check

# Check and prompt to install
python3 scripts/update.py

# Update without prompting
python3 scripts/update.py --yes

# Show full changelog
python3 scripts/update.py --changelog
```

### What It Does
1. Runs `git fetch --tags` to check the remote for new commits
2. Shows the current and latest version numbers
3. Lists what changed (commit summaries)
4. Warns if a **MAJOR** version bump requires reading migration notes
5. Runs `git pull --ff-only` if confirmed

### Pinning a version
A `.toolkit-pin` file containing a git ref (usually a release tag such as
`v3.15.0`) pins the clone to that ref. Put it in the consuming project root,
next to the `organisation/` clone; a pin inside the clone works as a fallback.
While pinned, `update.py` checks out the pinned ref instead of following
`main`; delete the file and run `update.py` again to resume normal updates.

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

## Requirements
- Python 3.9+ (no external dependencies)
- Run from the repo root or provide the full path to the script
- `update.py` requires the repo to have been cloned via git (not downloaded as a ZIP)
