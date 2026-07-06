# Project Workflow: Golden Sample

> Created: 2026-01-01 | Maintained by: Project Manager / Team Lead

## Quality Gates (Level 4: Large-Scale Engineering)
<!-- Activated by the project classification in project-brief.md.
     Every gate must pass before the project can be closed. -->

- [ ] **Architecture:** architecture.md plus decision records; scalability and failure-mode design are mandatory
- [ ] **Testing:** Full test pyramid plus performance, load, and security testing
- [ ] **Security:** Level 3 baseline plus penetration testing, compliance review, and audit logging
- [ ] **Review:** Two reviewers per PR; CTO-level architecture sign-off; mandatory security sign-off
- [ ] **Writing:** Validator pass plus mandatory editorial review of all external documents, sign-off recorded in handover notes

## Execution Model
Tasks marked `[SEQUENTIAL]` must wait for the previous step to complete.
Tasks marked `[PARALLEL]` can run simultaneously.

## Workflow Steps

<!-- Fill in the ordered task chain across team members.
     Example structure below; replace with your actual project tasks. -->

```
1. [SEQUENTIAL] PM: Define goals, KPIs, and acceptance criteria
2. [SEQUENTIAL] UX Researcher: User research and journey mapping
3. [PARALLEL]   Lead Designer: Wireframes and layout strategy
3. [PARALLEL]   Content Strategist: Copy and messaging
4. [SEQUENTIAL] Lead Designer: Final UI and design handoff
5. [SEQUENTIAL] Lead Engineer: Implementation
6. [SEQUENTIAL] QA Engineer: Testing and verification
7. [SEQUENTIAL] PM: Final review and deployment sign-off
```

## Task Breakdown (by lifecycle stage)
<!-- The six-stage Software Delivery Lifecycle is defined in the toolkit's INITIALIZE.md.
     Stages 1 and 2 (Discovery, Planning) are largely completed at initialization;
     record any remaining planning tasks under Stage 2. -->

### Stage 2: Planning (remaining tasks)
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 1 | [FILL IN] | [FILL IN] | SEQUENTIAL | none | Not Started |

### Stage 3: Implementation
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 2 | [FILL IN] | [FILL IN] | SEQUENTIAL | #1 | Not Started |

### Stage 4: Verification
<!-- The Quality Gates above are the exit criteria for this stage. -->
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 3 | [FILL IN] | [FILL IN] | SEQUENTIAL | #2 | Not Started |

### Stage 5: Deployment
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 4 | [FILL IN] | [FILL IN] | SEQUENTIAL | #3 | Not Started |

### Stage 6: Operations
<!-- Monitoring, support, and maintenance. Record the long-term owner in
     doc/handover/consolidated_handover.md before closure. -->
| # | Task | Owner | Type | Depends On | Status |
|---|------|-------|------|------------|--------|
| 5 | [FILL IN] | [FILL IN] | SEQUENTIAL | #4 | Not Started |

## Completion Criteria
<!-- What must be true before the project is considered done? -->
- [ ] All quality gates above pass
- [ ] [FILL IN]
