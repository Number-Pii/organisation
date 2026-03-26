# Number Pii — Organisation

> The virtual organisational structure for Number Pii — a fully-staffed, elite team built to help sole traders, startups, and SMEs grow through digital solutions. This repository is the single source of truth for team composition, role definitions, reporting lines, and operational governance.

Number Pii is a **software company and technology consultancy** focused on helping sole traders, startups, and SMEs grow through digital solutions. The company operates across three pillars:

| Pillar | What They Do |
|--------|-------------|
| **Products** | Build proprietary software — flagship product is **Thirty X**, a Business Operating System |
| **Services** | Web app, mobile app, and custom software development |
| **Consultancy** | Digital transformation & technology strategy advisory |

This document set covers every department — from Executive Leadership through Engineering, Product & Design, Sales & Consultancy, Growth & Marketing, and Operations — reflecting the company as a complete, fully-staffed virtual operation.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Departments](#departments)
- [Organisational Philosophy](#organisational-philosophy)
- [How to Use This Repository](#how-to-use-this-repository)
- [Contributing](#contributing)

---

## Overview

This repository contains the complete organisational blueprint for Number Pii — role-by-role documentation, reporting structures, delegation models, and approval authority matrices.

**What it covers:**

- Role definitions for every position in the company
- Skills, responsibilities, and project involvement per role
- The full org chart with reporting lines
- Project delegation: who leads, who executes, who approves
- Approval authority levels for every decision type
- Structural principles and hiring standards

---

## Repository Structure

```
organisation/
├── Teams/
│   ├── organisation.md                        # Master org chart, philosophy, delegation model
│   ├── 01-Executive-Leadership/               # CEO, CTO, CPO, CMO, COO, Chief of Staff, VP Sales
│   ├── 02-Engineering/                        # All engineering roles (~18–22 people)
│   ├── 03-Product-Design/                     # Product managers, designers, UX researcher, analyst
│   ├── 04-Sales-Consultancy/                  # Consultants, BDMs, account managers
│   ├── 05-Growth-Marketing/                   # Content, SEO, social, performance marketing
│   ├── 06-Operations/                         # Finance, people & talent, operations, facilities
│   └── skills/                                # 1,294 AI skill modules
├── scripts/
│   ├── audit_skills.py                        # Skill coverage auditor
│   ├── init_project.py                        # Project doc/ scaffolder
│   └── README.md                              # Script usage docs
├── CLAUDE.md                                  # Claude Code context + Initialize Protocol
├── GEMINI.md                                  # Gemini CLI context (identical to CLAUDE.md)
└── README.md                                  # This file
```

---

## Departments

### 01 — Executive Leadership

| Role | File |
|------|------|
| CEO / Founder | [CEO-Founder.md](Teams/01-Executive-Leadership/CEO-Founder.md) |
| CTO | [CTO.md](Teams/01-Executive-Leadership/CTO.md) |
| CPO | [CPO.md](Teams/01-Executive-Leadership/CPO.md) |
| CMO / VP Growth | [CMO-VP-Growth.md](Teams/01-Executive-Leadership/CMO-VP-Growth.md) |
| COO | [COO.md](Teams/01-Executive-Leadership/COO.md) |
| Chief of Staff | [Chief-of-Staff.md](Teams/01-Executive-Leadership/Chief-of-Staff.md) |
| VP Sales & Consultancy | [VP-Sales-Consultancy.md](Teams/01-Executive-Leadership/VP-Sales-Consultancy.md) |

### 02 — Engineering (~18–22 people)

Split into two verticals to protect product development from client work:

| Role | File |
|------|------|
| VP Product Engineering | [VP-Product-Engineering.md](Teams/02-Engineering/VP-Product-Engineering.md) |
| VP Client Engineering | [VP-Client-Engineering.md](Teams/02-Engineering/VP-Client-Engineering.md) |
| Engineering Manager | [Engineering-Manager.md](Teams/02-Engineering/Engineering-Manager.md) |
| Lead Frontend Engineer | [Lead-Frontend-Engineer.md](Teams/02-Engineering/Lead-Frontend-Engineer.md) |
| Senior Frontend Engineer | [Senior-Frontend-Engineer.md](Teams/02-Engineering/Senior-Frontend-Engineer.md) |
| Lead Backend Engineer | [Lead-Backend-Engineer.md](Teams/02-Engineering/Lead-Backend-Engineer.md) |
| Senior Backend Engineer | [Senior-Backend-Engineer.md](Teams/02-Engineering/Senior-Backend-Engineer.md) |
| Senior Full-Stack Engineer | [Senior-Full-Stack-Engineer.md](Teams/02-Engineering/Senior-Full-Stack-Engineer.md) |
| Lead Web Developer | [Lead-Web-Developer.md](Teams/02-Engineering/Lead-Web-Developer.md) |
| Senior Web Developer | [Senior-Web-Developer.md](Teams/02-Engineering/Senior-Web-Developer.md) |
| Lead Mobile Developer | [Lead-Mobile-Developer.md](Teams/02-Engineering/Lead-Mobile-Developer.md) |
| Senior Mobile Developer | [Senior-Mobile-Developer.md](Teams/02-Engineering/Senior-Mobile-Developer.md) |
| Senior Software Engineer (Custom) | [Senior-Software-Engineer-Custom.md](Teams/02-Engineering/Senior-Software-Engineer-Custom.md) |
| Head of DevOps & Infrastructure | [Head-DevOps-Infrastructure.md](Teams/02-Engineering/Head-DevOps-Infrastructure.md) |
| Senior DevOps Engineer | [Senior-DevOps-Engineer.md](Teams/02-Engineering/Senior-DevOps-Engineer.md) |
| Senior Cloud Engineer | [Senior-Cloud-Engineer.md](Teams/02-Engineering/Senior-Cloud-Engineer.md) |
| Head of QA & Reliability | [Head-QA-Reliability.md](Teams/02-Engineering/Head-QA-Reliability.md) |
| Senior QA Engineer | [Senior-QA-Engineer.md](Teams/02-Engineering/Senior-QA-Engineer.md) |
| QA Automation Engineer | [QA-Automation-Engineer.md](Teams/02-Engineering/QA-Automation-Engineer.md) |
| Head of Information Security | [Head-Information-Security.md](Teams/02-Engineering/Head-Information-Security.md) |
| Senior Security Engineer | [Senior-Security-Engineer.md](Teams/02-Engineering/Senior-Security-Engineer.md) |
| Security Analyst | [Security-Analyst.md](Teams/02-Engineering/Security-Analyst.md) |

### 03 — Product & Design (~6 people)

| Role | File |
|------|------|
| Senior PM — Thirty X | [Senior-Product-Manager-ThirtyX.md](Teams/03-Product-Design/Senior-Product-Manager-ThirtyX.md) |
| Product Manager — Future Products | [Product-Manager-Future.md](Teams/03-Product-Design/Product-Manager-Future.md) |
| Lead Product Designer | [Lead-Product-Designer.md](Teams/03-Product-Design/Lead-Product-Designer.md) |
| Senior Product Designer | [Senior-Product-Designer.md](Teams/03-Product-Design/Senior-Product-Designer.md) |
| UX Researcher | [UX-Researcher.md](Teams/03-Product-Design/UX-Researcher.md) |
| Product Analyst | [Product-Analyst.md](Teams/03-Product-Design/Product-Analyst.md) |

### 04 — Sales & Consultancy (~7 people)

| Role | File |
|------|------|
| Head of Consultancy | [Head-of-Consultancy.md](Teams/04-Sales-Consultancy/Head-of-Consultancy.md) |
| Principal Consultant — Digital Transformation | [Principal-Consultant-Digital-Transformation.md](Teams/04-Sales-Consultancy/Principal-Consultant-Digital-Transformation.md) |
| Principal Consultant — Technology Strategy | [Principal-Consultant-Technology-Strategy.md](Teams/04-Sales-Consultancy/Principal-Consultant-Technology-Strategy.md) |
| Head of Business Development | [Head-of-Business-Development.md](Teams/04-Sales-Consultancy/Head-of-Business-Development.md) |
| Senior Business Development Manager | [Senior-Business-Development-Manager.md](Teams/04-Sales-Consultancy/Senior-Business-Development-Manager.md) |
| Business Development Representative | [Business-Development-Representative.md](Teams/04-Sales-Consultancy/Business-Development-Representative.md) |
| Account Manager | [Account-Manager.md](Teams/04-Sales-Consultancy/Account-Manager.md) |

### 05 — Growth & Marketing (~5–6 people)

| Role | File |
|------|------|
| Head of Content & SEO | [Head-Content-SEO.md](Teams/05-Growth-Marketing/Head-Content-SEO.md) |
| Senior Content Strategist | [Senior-Content-Strategist.md](Teams/05-Growth-Marketing/Senior-Content-Strategist.md) |
| SEO Specialist | [SEO-Specialist.md](Teams/05-Growth-Marketing/SEO-Specialist.md) |
| Community & Brand Manager | [Community-Brand-Manager.md](Teams/05-Growth-Marketing/Community-Brand-Manager.md) |
| Performance Marketing Manager | [Performance-Marketing-Manager.md](Teams/05-Growth-Marketing/Performance-Marketing-Manager.md) |
| Social Media Manager | [Social-Media-Manager.md](Teams/05-Growth-Marketing/Social-Media-Manager.md) |

### 06 — Operations (~5 people)

| Role | File |
|------|------|
| Head of Finance | [Head-of-Finance.md](Teams/06-Operations/Head-of-Finance.md) |
| Head of People & Talent | [Head-of-People-Talent.md](Teams/06-Operations/Head-of-People-Talent.md) |
| Talent Acquisition Specialist | [Talent-Acquisition-Specialist.md](Teams/06-Operations/Talent-Acquisition-Specialist.md) |
| Operations Manager | [Operations-Manager.md](Teams/06-Operations/Operations-Manager.md) |
| Office / Facilities Manager | [Office-Facilities-Manager.md](Teams/06-Operations/Office-Facilities-Manager.md) |

---

## Organisational Philosophy

Number Pii operates at an uncompromising standard: **we only hire the top 1% of professionals in their field**.

| Principle | Detail |
|-----------|--------|
| **Products Ring-Fenced** | Product engineering is dedicated — client work has its own team and never cannibalises product development |
| **Elite Services** | Senior engineers deliver client projects at a premium level, backed by dedicated leadership |
| **Consultancy is Expert-Led** | Principal consultants with recognised domain expertise, not generalist advisors |
| **Security by Design** | Dedicated InfoSec team reviews every product and client delivery |
| **Seniority Over Volume** | One Staff Engineer > two mid-level. We don't hire to fill boxes |
| **Remote-First, Global Talent** | Geography is not a constraint — the top 1% are hired wherever they are |
| **Pay at 90th Percentile** | Elite people demand elite compensation |

For the full org chart, delegation model, and approval authority matrix, see [Teams/organisation.md](Teams/organisation.md).

---

## How to Use This Repository

**For hiring managers** — Each role file contains the full job brief: responsibilities, required skills, reporting line, and project involvement. Use it as the source of truth when opening a role.

**For new hires** — Read your role file, then `organisation.md` to understand where you sit in the structure, who you report to, and what you can approve independently.

**For project leads** — Consult the *Project Delegation Model* in `organisation.md` to determine who leads, who executes, and who signs off for any given project type.

**For leadership** — The *Approval Authority Matrix* in `organisation.md` defines decision-making boundaries for every level of the organisation.

---

## Using With AI Coding Assistants

### Initialize (Claude or Gemini)
Clone or download this repo into your project folder, then tell your AI assistant:
```
initialize CLAUDE.md
```
or (for Gemini CLI):
```
initialize GEMINI.md
```

The assistant will:
1. Welcome you as Number Pii
2. Collect your project brief
3. Assign the right team members from `Teams/`
4. Run `scripts/init_project.py` to scaffold your `doc/` folder
5. Fill in project documentation (brief, workflow, version control, handover)

### Skill Linking Convention
Every role file now has three layers:
- **Core Skills** — listed with inline `(@skill-name)` references
- **Technical Skills** — listed with inline `(@skill-name)` references
- **Agent Skills** — curated `@skill-name` list for direct invocation

Invoke any skill: `@skill-name [your task]`
Example: `@security-audit review this authentication implementation`

### Auditing Skill Coverage
```bash
python3 scripts/audit_skills.py --report
```
Generates a full report of which role bullets are linked and which skills are unused.

### Cross-Platform Support
Both `CLAUDE.md` and `GEMINI.md` are kept in sync with identical content.
- **Claude Code** reads `CLAUDE.md` automatically
- **Gemini CLI** reads `GEMINI.md` automatically
- Both support the same `initialize` command and follow the same protocol

---

## Keeping Up to Date

When this toolkit is updated, you can pull the latest version without affecting any of your existing projects.

**Your project files (`doc/`) live in your own project repo — they are never touched by a toolkit update.**

### Check for updates
```bash
python3 scripts/update.py --check
```

### Install an update
```bash
python3 scripts/update.py
```

### What changes between versions
See [CHANGELOG.md](CHANGELOG.md) for full release notes, or run:
```bash
python3 scripts/update.py --changelog
```

### Version types
| Version bump | What it means | Action needed |
|---|---|---|
| PATCH `3.1.x` | Wording fixes, role/skill updates | None — update freely |
| MINOR `3.x.0` | New protocol steps or features | Read changelog before new sessions |
| MAJOR `x.0.0` | Initialize Protocol restructured | Read migration notes before re-initializing |

> **Note:** Updates require cloning via git. If you downloaded this repo as a ZIP, re-clone it to enable updates:
> `git clone https://github.com/olatunbosun-iyare/organisation.git`

---

## Contributing

All changes to this repository require review by the relevant department head and sign-off from the CEO or Chief of Staff for structural changes.

1. Create a branch from `main`
2. Make your changes
3. Open a pull request with a clear description of what changed and why
4. Get approval from the relevant stakeholder before merging

> Document Version: 3.0 · Revised: 25 March 2026 · Author: Number Pii Leadership
