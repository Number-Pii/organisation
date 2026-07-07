"""Unit tests for scripts/check_plugin.py against a fixture plugin tree."""

import json

import pytest

import check_plugin

PROTECT_MAIN = "#!/usr/bin/env python3\n# main-branch protection\n"

HOOKS_JSON = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": (
                            'python3 "${CLAUDE_PLUGIN_ROOT}'
                            '/hooks/protect_main.py"'
                        ),
                    }
                ],
            }
        ]
    }
}


def make_repo(tmp_path):
    """Build a minimal valid plugin tree; tests then break one piece."""
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "np", "version": "3.19.1"}), encoding="utf-8")
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "hooks.json").write_text(
        json.dumps(HOOKS_JSON), encoding="utf-8")
    (tmp_path / "hooks" / "protect_main.py").write_text(
        PROTECT_MAIN, encoding="utf-8")
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "claude-protect-main.py").write_text(
        PROTECT_MAIN, encoding="utf-8")
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "init.md").write_text(
        "# /init\n\nRun the Initialize Protocol.\n", encoding="utf-8")
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "np-lead-backend-engineer.md").write_text(
        "---\nname: np-lead-backend-engineer\n---\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo(tmp_path, monkeypatch):
    make_repo(tmp_path)
    monkeypatch.setattr(check_plugin, "REPO_ROOT", tmp_path)
    return tmp_path


def run_main():
    with pytest.raises(SystemExit) as exc:
        check_plugin.main()
    return exc.value.code


def test_valid_tree_passes(repo):
    assert run_main() == 0


def test_real_repo_passes():
    """The checked-in packaging must always validate."""
    assert not (
        check_plugin.check_manifest()
        + check_plugin.check_hooks()
        + check_plugin.check_command()
        + check_plugin.check_agents()
        + check_plugin.check_protect_main_copies()
    )


def test_malformed_manifest_fails(repo):
    (repo / ".claude-plugin" / "plugin.json").write_text(
        "{not json", encoding="utf-8")
    assert run_main() == 1


def test_manifest_missing_version_fails(repo):
    (repo / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "np"}), encoding="utf-8")
    assert run_main() == 1


def test_malformed_hooks_json_fails(repo):
    (repo / "hooks" / "hooks.json").write_text("[broken", encoding="utf-8")
    assert run_main() == 1


def test_hook_referencing_missing_script_fails(repo):
    (repo / "hooks" / "protect_main.py").unlink()
    assert run_main() == 1


def test_hooks_without_plugin_root_refs_fails(repo):
    (repo / "hooks" / "hooks.json").write_text(
        json.dumps({"hooks": {}}), encoding="utf-8")
    assert run_main() == 1


def test_empty_command_file_fails(repo):
    (repo / "commands" / "init.md").write_text("\n", encoding="utf-8")
    assert run_main() == 1


def test_no_agents_fails(repo):
    (repo / "agents" / "np-lead-backend-engineer.md").unlink()
    assert run_main() == 1


def test_protect_main_drift_fails(repo):
    (repo / "templates" / "claude-protect-main.py").write_text(
        PROTECT_MAIN + "# drifted\n", encoding="utf-8")
    assert run_main() == 1
