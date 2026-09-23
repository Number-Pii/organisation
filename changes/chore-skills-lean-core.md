---
bump: minor
section: Removed
---
- **The skills library is cut from 1,291 skills (41 MB) to 54 reviewed ones
  (5 MB).** A skill stays only when it gives a frontier model something it
  lacks: bundled scripts, tool- or API-specific knowledge, a Number Pii
  process, or the canonical approach to a topic. Removed:
  - persona prompts ("You are an expert X") and filler stubs
  - exact and near duplicates
  - off-charter and non-English skills
  - skills that only work through the Rube/Composio connector
  - skills that told agents to skip permissions, push, or pipe installers
    into a shell

  The full library is tagged `v3-skills-full`:
  `git checkout v3-skills-full -- Teams/skills/<name>` restores any skill.

### Changed
- **Every kept skill has a reviewed risk and a review date.** Each carries
  `risk: low|medium|high` and `last_reviewed`, and `audit_skills.py` now fails
  without them.
- **Role files keep their prose.** Their `@skill` references point only at
  kept skills, and a role with no specific skill points to `find_skill.py`.
- **The TDD and systematic-debugging skills explain their rules.** Their
  "Iron Law" sections now state the practice and the reason for it, not
  absolutes. References to skills outside the library are fixed.
- **The skill eval tasks target kept skills.**

### Removed
- `scripts/generate_skill_frontmatter.py` (the backfill it served is done),
  `.gitattributes` (every entry pointed at a removed skill), and both duplicate
  workflow-bundle READMEs.
