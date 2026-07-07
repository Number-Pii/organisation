"""Tests for Phase 5: org.json, generated agents, plugin packaging, evals, handover drafts."""

import json
from pathlib import Path

import build_agents
import build_org
from draft_handover import draft_entry, last_entry_date
from run_evals import parse_tasks

REPO_ROOT = Path(__file__).resolve().parent.parent


# ── org.json generation ──────────────────────────────────────────────────────

ROLE_MD = """# Example Engineer

## Position Details
- **Department:** Engineering (Product Engineering)
- **Reports To:** Engineering Manager
- **Direct Reports:** None
- **Employment Type:** Full-time

## Role Summary
Builds examples.

## Core Skills
- Example building (@postgresql)

## Approval Authority
- **Can approve:** Example merges
- **Needs approval from:** Engineering Manager (big examples)

## Agent Skills
- @postgresql: databases
- @api-design-principles: APIs
"""


def test_parse_role_extracts_structure(tmp_path):
    md = tmp_path / "Example-Engineer.md"
    md.write_text(ROLE_MD, encoding="utf-8")
    import build_org as bo
    orig = bo.REPO_ROOT
    bo.REPO_ROOT = tmp_path
    try:
        role = bo.parse_role(md, "02-Engineering", "Engineering")
    finally:
        bo.REPO_ROOT = orig
    assert role["title"] == "Example Engineer"
    assert role["reports_to"] == "Engineering Manager"
    assert role["can_approve"] == "Example merges"
    assert role["needs_approval_from"].startswith("Engineering Manager")
    assert role["agent_skills"] == ["api-design-principles", "postgresql"]


def test_org_json_current_and_complete():
    org = json.loads((REPO_ROOT / "Teams" / "org.json").read_text(encoding="utf-8"))
    assert len(org["departments"]) == 6
    assert len(org["roles"]) == 53
    assert build_org.render(build_org.collect_org()) == \
        (REPO_ROOT / "Teams" / "org.json").read_text(encoding="utf-8")


# ── generated agents ─────────────────────────────────────────────────────────

def test_agents_match_their_role_files():
    files = build_agents.build_all()
    assert len(files) == len(build_agents.CORE_ROLES)
    for path, content in files.items():
        assert path.exists(), f"{path} missing; run build_agents.py"
        assert path.read_text(encoding="utf-8") == content
        assert "delegated execution authority only" in content
        assert "## Authority Boundaries" in content


def test_agent_slugs():
    assert build_agents.slugify("Head of Information Security") == "head-of-information-security"
    assert build_agents.slugify("QA Automation Engineer") == "qa-automation-engineer"


# ── plugin packaging ─────────────────────────────────────────────────────────

def test_plugin_manifest_version_matches_toolkit():
    manifest = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert manifest["version"] == version
    assert manifest["name"] == "np"


def test_plugin_hook_is_identical_to_scaffold_template():
    """One hook, two delivery channels; drift between them is a bug."""
    template = (REPO_ROOT / "templates" / "claude-protect-main.py").read_text(encoding="utf-8")
    plugin = (REPO_ROOT / "hooks" / "protect_main.py").read_text(encoding="utf-8")
    assert template == plugin


def test_plugin_hooks_config_points_at_plugin_root():
    hooks = json.loads((REPO_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    command = hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert "${CLAUDE_PLUGIN_ROOT}" in command and "protect_main.py" in command


# ── eval task parsing ────────────────────────────────────────────────────────

def test_parse_tasks_reads_all_fields(tmp_path):
    md = tmp_path / "demo.md"
    md.write_text(
        "# Demo\n\n## Task: one\n- **Skill:** @postgresql\n- **Prompt:** Do a thing.\n"
        "- **Rubric:**\n  - names the thing\n  - does the thing\n\n"
        "## Task: incomplete\n- **Skill:** @x\n- **Rubric:**\n  - never parsed (no prompt)\n",
        encoding="utf-8",
    )
    tasks = parse_tasks(md)
    assert len(tasks) == 1
    assert tasks[0] == {"slug": "one", "skill": "postgresql", "prompt": "Do a thing.",
                        "rubric": ["names the thing", "does the thing"]}


def test_shipped_task_files_parse_and_reference_real_skills():
    tasks_dir = REPO_ROOT / "evals" / "tasks"
    skills_dir = REPO_ROOT / "Teams" / "skills"
    parsed = [(f.stem, t) for f in sorted(tasks_dir.glob("*.md")) for t in parse_tasks(f)]
    assert len(parsed) >= 9
    for domain, task in parsed:
        assert (skills_dir / task["skill"]).is_dir(), \
            f"{domain}/{task['slug']} references missing skill @{task['skill']}"
        assert len(task["rubric"]) >= 3


# ── handover drafting ────────────────────────────────────────────────────────

def test_draft_entry_groups_by_commit_type():
    commits = [
        ("abc1234", "feat(api): add webhook endpoint"),
        ("def5678", "fix: correct retry backoff"),
        ("aaa1111", "update readme"),
    ]
    entry = draft_entry(commits, "2026-07-07")
    assert entry.startswith("### 2026-07-07")
    lines = entry.splitlines()
    assert "- feat: add webhook endpoint (abc1234)" in lines
    assert "- fix: correct retry backoff (def5678)" in lines
    assert "- other: update readme (aaa1111)" in lines
    assert lines.index("- feat: add webhook endpoint (abc1234)") < \
        lines.index("- other: update readme (aaa1111)")


def test_last_entry_date_finds_most_recent(tmp_path):
    f = tmp_path / "handover-notes.md"
    f.write_text("## Work Completed\n\n### 2026-05-01\n- x\n\n### 2026-06-15\n- y\n",
                 encoding="utf-8")
    assert last_entry_date(f) == "2026-06-15"
    assert last_entry_date(tmp_path / "absent.md") is None
