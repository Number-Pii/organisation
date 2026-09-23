"""Tests for scripts/migrate_consumer.py against a real v3.19.1 scaffold.

tests/fixtures/v3-project/ is init_project.py output from v3.19.1, plus an
appended addendum in AGENTS.md, a PRD, and a qa/ folder, the shape of the real
consumer projects.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

import docs
import migrate_consumer as mc

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "v3-project"


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "shop"
    shutil.copytree(FIXTURE, root)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}


def test_dry_run_writes_nothing(project):
    before = snapshot(project)
    assert mc.main(["--project", str(project)]) == 0
    assert snapshot(project) == before


def test_apply_moves_to_v4_layout(project):
    assert mc.main(["--project", str(project), "--apply"]) == 0
    agents = (project / "AGENTS.md").read_text()
    assert agents.startswith("# Legacy Shop\n")
    assert "Level 2 (Standard Application)" in agents
    assert agents.count("<!-- np:begin -->") == 1
    assert "The payments service is owned by the platform team." in agents
    assert "MANDATORY READING" not in agents
    for stub in ("CLAUDE.md", "GEMINI.md"):
        assert "@AGENTS.md" in (project / stub).read_text()

    state = (project / "doc" / "handover" / "STATE.md").read_text()
    assert state.startswith("---\nconsolidated_through: none\n---\n")
    assert "Consolidated Handover: Legacy Shop" in state
    assert "handover/engineering/handover-notes.md" in state
    assert not (project / "doc" / "handover" / "consolidated_handover.md").exists()
    assert (project / "doc" / "handover" / "engineering" / "handover-notes.md").exists()

    doc_map = (project / "doc" / "README.md").read_text()
    assert "`PRD.md`" in doc_map and "`qa/`" in doc_map
    assert doc_map.count("`handover/") == 2, "existing folders must not be listed twice"

    assert (project / ".githooks" / "pre-push").stat().st_mode & 0o111
    assert not (project / ".claude" / "hooks" / "context-checklist.md").exists()
    assert "SessionStart" not in (project / ".claude" / "settings.json").read_text()
    assert "worktree" in (project / ".claude" / "hooks" / "protect_main.py").read_text()
    assert "| Status |" in (project / "doc" / "workflow.md").read_text()

    assert docs.main(["--root", str(project), "check"]) == 0


def test_second_run_changes_nothing(project, capsys):
    mc.main(["--project", str(project), "--apply"])
    after = snapshot(project)
    capsys.readouterr()
    assert mc.main(["--project", str(project), "--apply"]) == 0
    assert snapshot(project) == after
    assert "Nothing to migrate." in capsys.readouterr().out


def test_hand_written_context_files_are_never_rewritten(project):
    hand = "# Shop: Project Context for AI Sessions\n\n> Hand-written — keep.\n"
    for name in ("CLAUDE.md", "AGENTS.md"):
        (project / name).write_text(hand)
    mc.main(["--project", str(project), "--apply"])
    for name in ("CLAUDE.md", "AGENTS.md"):
        assert (project / name).read_text() == hand
    assert "@AGENTS.md" in (project / "GEMINI.md").read_text()


def test_strip_status_is_opt_in(project):
    mc.main(["--project", str(project), "--apply", "--strip-status"])
    workflow = (project / "doc" / "workflow.md").read_text()
    assert "| Status |" not in workflow and "| Depends On |" in workflow


def test_refuses_to_run_on_the_toolkit():
    toolkit = Path(__file__).resolve().parent.parent
    assert mc.main(["--project", str(toolkit)]) == 1


def test_links_to_the_old_handover_are_repointed(project):
    prd = project / "doc" / "PRD.md"
    prd.write_text(prd.read_text() + "\nState: [doc/handover/consolidated_handover.md](handover/consolidated_handover.md).\n")
    notes = project / "doc" / "handover" / "engineering" / "handover-notes.md"
    notes.write_text(notes.read_text() + "\nSee [consolidated_handover.md](../consolidated_handover.md).\n")
    archive = project / "doc" / "handover" / "archive" / "2026-05.md"
    archive.write_text("Old: [x](../consolidated_handover.md)\n")
    mc.main(["--project", str(project), "--apply"])
    assert "[doc/handover/STATE.md](handover/STATE.md)" in prd.read_text()
    assert "[STATE.md](../STATE.md)" in notes.read_text()
    assert "consolidated_handover.md" in archive.read_text(), "archives stay as history"
    assert docs.main(["--root", str(project), "check"]) == 0


def test_v3_parallel_rules_are_replaced_only_while_unedited(project):
    mc.main(["--project", str(project), "--apply"])
    vc = (project / "doc" / "version_control.md").read_text()
    assert "## Parallel Work" in vc and "## Concurrent Sessions" not in vc
    assert "check_handover.py" not in vc


def test_edited_concurrency_section_is_left_alone(project):
    vc = project / "doc" / "version_control.md"
    vc.write_text(vc.read_text().replace(
        "- Check handover freshness before starting: `python3 organisation/scripts/check_handover.py`",
        "- Our own rule: ping the channel before starting."))
    mc.main(["--project", str(project), "--apply"])
    assert "Our own rule: ping the channel" in vc.read_text()
