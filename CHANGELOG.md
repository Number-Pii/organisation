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
  then re-clone: `git clone https://github.com/olatunbosun-iyare/organisation.git organisation`

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
