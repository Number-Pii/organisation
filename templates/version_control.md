# Version Control: $project_name

> Created: $today | Owner: Lead / Senior Engineer on this project

## Branching Strategy

<!-- Choose and document the strategy for this project.
     Options: Git Flow, GitHub Flow, trunk-based, feature branch, etc.
     Suggested for Level $level ($level_name): $level_vc_strategy -->

### Strategy: [FILL IN]

```
main                  ← production-ready, protected
├── develop           ← integration branch (if using Git Flow)
│   ├── feature/xxx   ← feature branches
│   ├── fix/xxx       ← bug fix branches
│   └── release/x.x  ← release preparation (if needed)
└── hotfix/xxx        ← critical production fixes
```

## Branch Naming Convention
```
feature/[ticket-id]-short-description   e.g. feature/PROJ-42-user-auth
fix/[ticket-id]-short-description       e.g. fix/PROJ-55-login-redirect
release/x.x.x                           e.g. release/1.2.0
hotfix/short-description                e.g. hotfix/payment-crash
```

## Commit Message Format
```
type(scope): short description

types: feat | fix | docs | style | refactor | test | chore
```

## Pull Request Rules (Level $level: $level_name)
<!-- The review rules below are set by the project classification level.
     Raising or lowering them is a scope change: it needs user/founder approval. -->
$pr_rules_block
- [ ] All CI checks must pass (tests, lint, build)
- [ ] Branch must be up to date with target before merge
- [ ] PR description must reference ticket/issue
- [ ] No direct pushes to `main` (branch protection enabled)

## Concurrent Sessions
Rules for running more than one AI session (or contributor) on this project at once:
- **One active session per branch.** A second session starts its own branch; two sessions never share a working branch.
- **Handover notes are append-only.** Add a new dated entry under Work Completed; never rewrite or delete another session's entries.
- **`consolidated_handover.md` has one writer at a time:** the team lead consolidates after parallel work merges, not during it.
- Check handover freshness before starting: `python3 organisation/scripts/check_handover.py`

## Release Process (Level $level: $level_name)
<!-- Adjust the mechanics to this project, but keep the sign-off requirements:
     they come from the classification level. -->
$level_release_process

## Repository
- **Repo URL:** [FILL IN]
- **Primary branch:** main
- **CI/CD:** [FILL IN, e.g. GitHub Actions]
- **Deployment:** [FILL IN]
