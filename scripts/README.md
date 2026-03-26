# Number Pii — Scripts

Two Python 3 scripts that automate deterministic work, saving tokens and time.

---

## `audit_skills.py` — Skill Coverage Auditor

Reports how well each role file's Core Skills and Technical Skills are linked to `@skill-name`
references from `Teams/skills/`.

### Usage
```bash
# Run from repo root
python3 scripts/audit_skills.py

# Plain output (no ANSI colour — good for Gemini CLI or CI)
python3 scripts/audit_skills.py --no-color

# Also write an audit_report.md file to scripts/
python3 scripts/audit_skills.py --report
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

## `init_project.py` — Project Scaffolder

Creates the standard `doc/` folder structure in any project directory. Run after your AI
coding assistant has determined the project brief and team assignment.

### Usage
```bash
# Basic — creates doc/ in the current directory
python3 /path/to/org/scripts/init_project.py --project-name "My Project"

# With specific departments (creates dept handover sub-folders)
python3 /path/to/org/scripts/init_project.py \
  --project-name "Client Landing Page" \
  --departments "engineering,design,marketing"

# Into a specific project directory
python3 /path/to/org/scripts/init_project.py \
  --project-name "API Build" \
  --departments "engineering" \
  --output-dir /path/to/my-project

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
| `--dry-run` | false | Preview the structure without creating files |

### What It Creates
```
doc/
├── project-brief.md          # Goals, scope, client, constraints, stakeholders
├── team-assignment.md        # Assigned team members and their responsibilities
├── workflow.md               # Step-by-step task chain (sequential + parallel)
├── version_control.md        # Git strategy, branching, PR rules
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
4. The new session has full context immediately — no re-explanation needed

---

## Requirements
- Python 3.9+ (no external dependencies)
- Run from the repo root or provide the full path to the script
