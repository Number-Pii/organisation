#!/usr/bin/env python3
"""
init_project.py: Number Pii Project Scaffolder

Creates the standard project scaffold in any project directory: the root
AGENTS.md (with the toolkit's managed block) and its CLAUDE.md and GEMINI.md
stubs, the doc/ tree, and the git and Claude Code guard hooks. Run it after the
brief, level, and team are agreed. It never overwrites an existing file.

Template content lives in templates/*.md at the toolkit root and is rendered
with string.Template ($variable placeholders). Wording changes are markdown
edits, not code edits.

Usage:
    python3 scripts/init_project.py --project-name "My Project"
    python3 scripts/init_project.py --project-name "Client Landing Page" --departments "engineering,design,marketing" --level 1
    python3 scripts/init_project.py --project-name "API Build" --departments "engineering" --output-dir /path/to/project --level 2
    python3 scripts/init_project.py --project-name "Inherited App" --departments "engineering" --output-dir /path/to/project --existing --level 3

Arguments:
    --project-name   Name of the project (used in file headers)
    --departments    Accepted for compatibility; handover is per branch since 4.0.0
    --output-dir     Directory to create doc/ in (default: current working directory)
    --level          Project classification level 1-4 (default: 2). Sets the quality gates
                     scaffolded into the doc files. Level 3+ adds architecture.md.
    --existing       Brownfield mode: adds codebase-assessment.md and an existing-product
                     section in doc/handover/STATE.md
    --no-claude-hooks  Skip the .claude/ guard hook (the git pre-push hook is always written)
    --dry-run        Preview what would be created without creating anything
"""

import argparse
from datetime import date
from pathlib import Path
from string import Template

TODAY = date.today().isoformat()

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"

# ── Project classification ────────────────────────────────────────────────────
# Each level activates a matching depth of documentation, architecture, testing,
# security, and review. The level is agreed with the user during Step 2c of the
# Initialize Protocol and recorded in doc/project-brief.md. The pr_rules and
# release_process entries render into doc/version_control.md, so the review
# depth the level demands is written into the branching contract itself.

LEVELS = {
    1: {
        "name": "Simple Task",
        "examples": "Landing pages, internal tools, automation scripts, API integrations, technical documentation",
        "team": "1-3 roles (PM + 1-2 specialists)",
        "documentation": "Core doc/ set only",
        "architecture": "No separate document; note key technical choices in workflow.md",
        "testing": "Manual verification plus smoke tests on critical paths",
        "security": "Secure defaults: secrets management, input validation, dependency hygiene",
        "review": "Self-review checklist plus one PR review",
        "writing": "Prose deliverables pass scripts/check_writing.py (self-check)",
        "vc_strategy": "GitHub Flow (single main, short-lived branches, PR per change)",
        "pr_rules": [
            "Self-review checklist completed before requesting review",
            "At least 1 peer review required before merge",
        ],
        "release_process": (
            "Deploy after the smoke tests pass. Tag the release and record the "
            "deployed version in the handover notes."
        ),
    },
    2: {
        "name": "Standard Application",
        "examples": "SaaS platforms, marketplaces, CRM systems, mobile applications",
        "team": "4-7 roles across 2-3 departments",
        "documentation": "Core doc/ set only",
        "architecture": "Lightweight design notes agreed before implementation (workflow.md Phase 1)",
        "testing": "Unit and integration tests on critical paths; CI required",
        "security": "Level 1 baseline plus dependency scanning and an authentication/authorisation review",
        "review": "One approving PR review; lead sign-off on releases",
        "writing": "Validator pass plus a lead read of client-facing prose",
        "vc_strategy": "GitHub Flow with required PR review and CI checks",
        "pr_rules": [
            "At least 1 approving peer review required before merge",
        ],
        "release_process": (
            "The team lead signs off every release. Tag the release, deploy through "
            "CI, and record the version and sign-off in the handover notes."
        ),
    },
    3: {
        "name": "Advanced System",
        "examples": "Multi-tenant SaaS, AI products, agentic systems, enterprise platforms, data pipelines",
        "team": "8-12 roles across 3-4 departments",
        "documentation": "Core doc/ set plus architecture.md",
        "architecture": "architecture.md completed and approved before implementation begins",
        "testing": "Unit, integration, and end-to-end suites; agreed coverage target; CI gates block merge",
        "security": "Level 2 baseline plus a threat model and a security review before each release",
        "review": "Lead engineer review on every PR; security sign-off on sensitive changes",
        "writing": "Validator pass plus Senior Content Strategist editorial review on client-facing deliverables",
        "vc_strategy": "GitHub Flow or Git Flow with protected main, required reviews, and CI gates",
        "pr_rules": [
            "Lead engineer review required on every PR",
            "Security sign-off required on sensitive changes (auth, data handling, secrets)",
        ],
        "release_process": (
            "A security review passes before each release. The lead engineer signs "
            "off, the release is tagged and deployed through the CI pipeline, and "
            "both sign-offs are recorded in the handover notes."
        ),
    },
    4: {
        "name": "Large-Scale Engineering",
        "examples": "National platforms, government systems, financial systems, healthcare systems, distributed architectures",
        "team": "Full team assignment from Teams/organisation.md",
        "documentation": "Core doc/ set plus architecture.md with decision records",
        "architecture": "architecture.md plus decision records; scalability and failure-mode design are mandatory",
        "testing": "Full test pyramid plus performance, load, and security testing",
        "security": "Level 3 baseline plus penetration testing, compliance review, and audit logging",
        "review": "Two reviewers per PR; CTO-level architecture sign-off; mandatory security sign-off",
        "writing": "Validator pass plus mandatory editorial review of all external documents, sign-off recorded in handover notes",
        "vc_strategy": "Git Flow with protected main and develop, multi-reviewer approval, and signed releases",
        "pr_rules": [
            "Two approving reviews required on every PR",
            "CTO-level sign-off required on architecture-affecting changes",
            "Security sign-off required before merge",
        ],
        "release_process": (
            "Releases are signed. Each release requires two approving reviews, "
            "CTO-level architecture sign-off, a passing security and compliance "
            "review, and an audit-log entry, all recorded before deployment."
        ),
    },
}


# ── Template rendering ────────────────────────────────────────────────────────

def load_template(name: str) -> Template:
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise SystemExit(
            f"ERROR: template not found: {path}\n"
            "  The templates/ folder ships with the toolkit; re-clone or update it."
        )
    return Template(path.read_text(encoding="utf-8"))


def load_raw(name: str) -> str:
    """A template used verbatim (shell scripts, the managed block): no placeholders."""
    return load_template(name).template


def render(name: str, **context) -> str:
    """Render templates/<name> with the given context; a missing placeholder
    raises KeyError so a template/code mismatch fails loudly."""
    return load_template(name).substitute(**context)


def level_context(level: int) -> dict:
    """Template variables derived from the classification level."""
    lv = LEVELS[level]
    pr_rules_block = "\n".join(f"- [ ] {rule}" for rule in lv["pr_rules"])
    return {
        "level": str(level),
        "level_name": lv["name"],
        "level_examples": lv["examples"],
        "level_team": lv["team"],
        "level_documentation": lv["documentation"],
        "level_architecture": lv["architecture"],
        "level_testing": lv["testing"],
        "level_security": lv["security"],
        "level_review": lv["review"],
        "level_writing": lv["writing"],
        "level_vc_strategy": lv["vc_strategy"],
        "level_release_process": lv["release_process"],
        "pr_rules_block": pr_rules_block,
    }


def build_files(project_name: str, departments: list[str], output_dir: Path,
                existing: bool = False, level: int = 2, today: str = TODAY,
                claude_hooks: bool = True) -> dict:
    """Return {path: rendered content} for the full scaffold. Pure function of
    its inputs so tests can compare output against golden files. `departments`
    is kept for compatibility: handover is per branch, not per department."""
    doc_dir = output_dir / "doc"
    handover_dir = doc_dir / "handover"

    ctx = {"project_name": project_name, "today": today, **level_context(level)}

    level4_note = ""
    if level == 4:
        level4_note = load_raw("level4-architecture-note.md")
    existing_section = load_raw("existing-context-section.md") if existing else ""

    files = {
        output_dir / "AGENTS.md": render("agents-root.md", agents_block=load_raw("agents-block.md"), **ctx),
        output_dir / "CLAUDE.md": load_raw("claude-stub.md"),
        output_dir / "GEMINI.md": load_raw("gemini-stub.md"),
        output_dir / ".githooks" / "pre-push": load_raw("pre-push"),
        doc_dir / "README.md":          render("doc-README.md", **ctx),
        doc_dir / "project-brief.md":   render("project-brief.md", **ctx),
        doc_dir / "team-assignment.md": render("team-assignment.md", **ctx),
        doc_dir / "workflow.md":        render("workflow.md", **ctx),
        doc_dir / "version_control.md": render("version_control.md", **ctx),
        doc_dir / "task-board.md":      render("task-board.md", **ctx),
        handover_dir / "STATE.md": render(
            "handover-state.md", existing_context_section=existing_section, **ctx),
        handover_dir / "entries" / "README.md": load_raw("handover-entries-README.md"),
    }

    # Claude Code catches commits on main inside the session, before git does.
    if claude_hooks:
        claude_dir = output_dir / ".claude"
        files[claude_dir / "settings.json"] = render("claude-settings.json", **ctx)
        files[claude_dir / "hooks" / "protect_main.py"] = load_raw("claude-protect-main.py")

    if level >= 3:
        files[doc_dir / "architecture.md"] = render(
            "architecture.md", level4_note=level4_note, **ctx)

    if existing:
        files[doc_dir / "codebase-assessment.md"] = render("codebase-assessment.md", **ctx)

    return files


# ── Scaffold ──────────────────────────────────────────────────────────────────

EXECUTABLE = {"pre-push"}


def scaffold(project_name: str, departments: list[str], output_dir: Path,
             dry_run: bool, existing: bool = False, level: int = 2,
             claude_hooks: bool = True):
    files = build_files(project_name, departments, output_dir,
                        existing=existing, level=level, claude_hooks=claude_hooks)

    if dry_run:
        print("\n[DRY RUN] Would create:")
        for path in sorted(files.keys()):
            print(f"  {path}")
        return

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            print(f"  [SKIP] {path.relative_to(output_dir)} already exists")
        else:
            path.write_text(content, encoding="utf-8")
            if path.name in EXECUTABLE:
                path.chmod(0o755)
            print(f"  [OK]   {path.relative_to(output_dir)}")

    print(f"\n✓ Scaffolded '{project_name}' in {output_dir}")
    print(f"  Classification: Level {level} ({LEVELS[level]['name']}). Quality gates are in doc/workflow.md.")
    print("  Next: describe the project at the top of AGENTS.md and fill in doc/.")
    print("  Enable the push guard once per clone: git config core.hooksPath .githooks")
    print("  and turn on branch protection for main in your hosting service.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold Number Pii project doc/ structure")
    parser.add_argument("--project-name",  required=True, help="Project name")
    parser.add_argument("--departments",   default="engineering",
                        help="Comma-separated dept names (default: engineering)")
    parser.add_argument("--output-dir",    default=".", help="Target directory (default: .)")
    parser.add_argument("--level",         type=int, choices=[1, 2, 3, 4], default=2,
                        help="Project classification level 1-4 (default: 2). Level 3+ adds architecture.md")
    parser.add_argument("--existing",      action="store_true",
                        help="Brownfield mode: add codebase-assessment.md and existing-product context")
    parser.add_argument("--no-claude-hooks", action="store_true",
                        help="Skip the .claude/ guard hook (the git pre-push hook is always written)")
    parser.add_argument("--dry-run",       action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    depts = [d.strip() for d in args.departments.split(",") if d.strip()]
    out   = Path(args.output_dir).resolve()

    # Safety check: prevent doc/ being created inside the organisation toolkit itself.
    if out == REPO_ROOT:
        print(
            "\nERROR: --output-dir points to the organisation toolkit itself.\n"
            "  doc/ must be created in your consuming project, not here.\n"
            f"  Toolkit root: {REPO_ROOT}\n"
            "  Use: --output-dir /path/to/your-project\n"
        )
        raise SystemExit(1)

    scaffold(
        project_name=args.project_name,
        departments=depts,
        output_dir=out,
        dry_run=args.dry_run,
        existing=args.existing,
        level=args.level,
        claude_hooks=not args.no_claude_hooks,
    )
