# {Role Title}

> **Reference template for all role files in `Teams/[department]/`.**
> When creating a new role, copy the sections below and fill in the blanks.
> Every role file **must** contain these seven sections in this order.

---

## Position Details
- **Department:** {e.g. Engineering — Product Engineering}
- **Reports To:** {role title of direct manager}
- **Direct Reports:** {titles, or "None"}
- **Employment Type:** {Full-time / Part-time / Contract}

## Role Summary
{One-paragraph description of what this role owns, who they work with, and the business outcome they are accountable for. Keep to 2–4 sentences.}

## Core Skills
{Human-readable competencies. Each bullet should end with one or more inline skill refs.}
- {competency} (@skill-one, @skill-two)
- {competency} (@skill-three)

## Technical Skills
{Specific tools, languages, frameworks, platforms. Each bullet should end with skill refs.}
- {technology / tool} (@skill-one)
- {technology / tool} (@skill-two)

## Project Involvement
| Project Type | Role in Project | Authority Level |
|---|---|---|
| {project type} | {lead / reviewer / contributor} | {Execute / Approve} |

## Approval Authority
- **Can approve:** {decisions this role signs off without escalation}
- **Needs approval from:** {who they escalate to and for what}

## Agent Skills
Invoke these skills when working as this role:
- @skill-name — {one-line description}

---

## Style Notes (do not include these in the final role file)

- **All three skill sections** (Core, Technical, Agent) must be present even if one is short — `scripts/audit_skills.py` parses section headings.
- **Skill naming:** `@skill-name` must match a folder in `Teams/skills/`. Run `python3 scripts/audit_skills.py` to verify.
- **Kebab-case filenames:** role files use `Role-Title.md` (hyphens, PascalCase words) matching the role's canonical title.
- **No boilerplate prose:** keep everything tight. The audit script treats `-` bullets as the semantic unit; narrative paragraphs between bullets will not be parsed.
