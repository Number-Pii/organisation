"""Tests for the enforcement layer: protect_main hook, .toolkit-pin, update_all."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import update as update_mod
import update_all

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_TEMPLATE = REPO_ROOT / "templates" / "claude-protect-main.py"


# ── protect_main.py hook ─────────────────────────────────────────────────────

def run_hook(cwd: Path, tool_name: str, command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": tool_name, "tool_input": {"command": command}})
    return subprocess.run(
        [sys.executable, str(HOOK_TEMPLATE)],
        input=payload, capture_output=True, text=True, cwd=cwd,
    )


def git_repo(tmp_path: Path, branch: str) -> Path:
    subprocess.run(["git", "init", "-q", "-b", branch, str(tmp_path)], check=True)
    return tmp_path


def test_hook_blocks_push_to_main_refspec(tmp_path):
    repo = git_repo(tmp_path, "feature/x")
    result = run_hook(repo, "Bash", "git push origin main")
    assert result.returncode == 2
    assert "protected branch" in result.stderr


def test_hook_blocks_commit_on_main(tmp_path):
    repo = git_repo(tmp_path, "main")
    result = run_hook(repo, "Bash", 'git commit -m "hotfix"')
    assert result.returncode == 2
    assert "doc/version_control.md" in result.stderr


def test_hook_blocks_push_while_on_main(tmp_path):
    repo = git_repo(tmp_path, "main")
    result = run_hook(repo, "Bash", "git push")
    assert result.returncode == 2


def test_hook_allows_feature_branch_flow(tmp_path):
    repo = git_repo(tmp_path, "feature/login")
    assert run_hook(repo, "Bash", 'git commit -m "wip"').returncode == 0
    assert run_hook(repo, "Bash", "git push -u origin feature/login").returncode == 0


def test_hook_allows_non_git_commands(tmp_path):
    repo = git_repo(tmp_path, "main")
    assert run_hook(repo, "Bash", "python3 -m pytest tests/").returncode == 0
    assert run_hook(repo, "Bash", "git status").returncode == 0


def test_hook_ignores_other_tools(tmp_path):
    repo = git_repo(tmp_path, "main")
    assert run_hook(repo, "Read", "git push origin main").returncode == 0


def test_hook_tolerates_malformed_input(tmp_path):
    result = subprocess.run(
        [sys.executable, str(HOOK_TEMPLATE)],
        input="not json", capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0


# ── update.py pin resolution ─────────────────────────────────────────────────

def test_read_pin_prefers_consumer_root(tmp_path, monkeypatch):
    clone = tmp_path / "organisation"
    clone.mkdir()
    (tmp_path / ".toolkit-pin").write_text("v3.15.0\n", encoding="utf-8")
    (clone / ".toolkit-pin").write_text("v3.14.0\n", encoding="utf-8")
    monkeypatch.setattr(update_mod, "REPO_ROOT", clone)
    ref, source = update_mod.read_pin()
    assert ref == "v3.15.0"
    assert source == tmp_path / ".toolkit-pin"


def test_read_pin_falls_back_to_clone(tmp_path, monkeypatch):
    clone = tmp_path / "organisation"
    clone.mkdir()
    (clone / ".toolkit-pin").write_text("v3.14.0\n", encoding="utf-8")
    monkeypatch.setattr(update_mod, "REPO_ROOT", clone)
    assert update_mod.read_pin() == ("v3.14.0", clone / ".toolkit-pin")


def test_read_pin_absent_or_empty(tmp_path, monkeypatch):
    clone = tmp_path / "organisation"
    clone.mkdir()
    monkeypatch.setattr(update_mod, "REPO_ROOT", clone)
    assert update_mod.read_pin() == ("", None)
    (clone / ".toolkit-pin").write_text("  \n", encoding="utf-8")
    assert update_mod.read_pin() == ("", None)


# ── update_all.py registry ───────────────────────────────────────────────────

def test_load_consumers_builds_clone_paths(tmp_path):
    registry = tmp_path / "consumers.json"
    registry.write_text(json.dumps({
        "base": str(tmp_path),
        "consumers": [{"name": "alpha", "path": "work/alpha"}],
    }), encoding="utf-8")
    consumers = update_all.load_consumers(registry)
    assert consumers == [{"name": "alpha", "clone": tmp_path / "work" / "alpha" / "organisation"}]


def test_load_consumers_missing_registry_exits(tmp_path):
    with pytest.raises(SystemExit):
        update_all.load_consumers(tmp_path / "absent.json")


def test_load_consumers_malformed_exits(tmp_path):
    registry = tmp_path / "consumers.json"
    registry.write_text("{not json", encoding="utf-8")
    with pytest.raises(SystemExit):
        update_all.load_consumers(registry)


def test_clone_version_and_pin_helpers(tmp_path):
    clone = tmp_path / "proj" / "organisation"
    clone.mkdir(parents=True)
    assert update_all.clone_version(clone) == ""
    (clone / "VERSION").write_text("3.16.0\n", encoding="utf-8")
    assert update_all.clone_version(clone) == "3.16.0"
    assert update_all.clone_pin(clone) == ""
    (clone.parent / ".toolkit-pin").write_text("v3.15.0\n", encoding="utf-8")
    assert update_all.clone_pin(clone) == "v3.15.0"
