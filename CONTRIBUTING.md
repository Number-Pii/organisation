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
2. Add a `SKILL.md` file (required) — see existing skills for format
3. Optionally add `scripts/`, `examples/`, or `resources/` subdirectories
4. Reference the skill in the relevant role file(s) if appropriate
5. Run `python3 scripts/audit_skills.py` to confirm the skill is detected

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

## Why the Mandatory Reading Protocol Exists

Past sessions have skipped project context files, expanded scope without permission, pushed directly to `main`, and created ad-hoc troubleshooting docs inside `doc/`. Every one of those failures traced back to an AI assistant treating the protocol as optional reading.

The Mandatory Reading Protocol in `CLAUDE.md` / `GEMINI.md` — and every Non-Negotiable Standard under it — is written as a hard rule precisely because soft guidance produced repeated regressions. When tempted to compress further, remember: the rules are short because they are terminal, not because they are flexible.
