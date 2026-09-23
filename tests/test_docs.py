"""Tests for scripts/docs.py: the documentation graph stays connected."""

import subprocess
from pathlib import Path

import docs
from init_project import scaffold

REPO_ROOT = Path(__file__).resolve().parent.parent


def project(tmp_path: Path) -> Path:
    scaffold("Demo", ["engineering"], tmp_path, dry_run=False, level=3, existing=True)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


def test_fresh_scaffold_passes(tmp_path):
    assert docs.main(["--root", str(project(tmp_path)), "check"]) == 0


def test_files_in_known_folders_need_no_index_edit(tmp_path):
    root = project(tmp_path)
    (root / "doc" / "decisions").mkdir()
    (root / "doc" / "decisions" / "2026-09-23-auth.md").write_text("# Auth\n\nUse OIDC.\n")
    assert docs.main(["--root", str(root), "check"]) == 0


def test_top_level_orphan_and_unknown_folder_fail(tmp_path, capsys):
    root = project(tmp_path)
    (root / "doc" / "debug-notes.md").write_text("# Notes\n")
    (root / "doc" / "qa").mkdir()
    (root / "doc" / "qa" / "plan.md").write_text("# Plan\n")
    assert docs.main(["--root", str(root), "check"]) == 1
    out = capsys.readouterr().out
    assert "doc/debug-notes.md" in out and "doc/qa/" in out


def test_broken_relative_link_fails(tmp_path, capsys):
    root = project(tmp_path)
    brief = root / "doc" / "project-brief.md"
    brief.write_text(brief.read_text() + "\nSee [the spec](specs/missing.md).\n")
    assert docs.main(["--root", str(root), "check"]) == 1
    assert "specs/missing.md" in capsys.readouterr().out


def test_summary_prefers_front_matter_then_first_paragraph(tmp_path):
    a = tmp_path / "a.md"
    a.write_text("---\nsummary: Short answer.\n---\n# A\n\nLonger text.\n")
    b = tmp_path / "b.md"
    b.write_text("# B\n\n<!-- note -->\n\nFirst real paragraph here.\n")
    assert docs.summary(a) == "Short answer."
    assert docs.summary(b) == "First real paragraph here."


def test_toolkit_itself_is_connected():
    assert docs.main(["--root", str(REPO_ROOT), "check"]) == 0
