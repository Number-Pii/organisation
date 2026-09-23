"""Unit tests for scripts/check_version.py against a fixture repo tree."""

import json

import pytest

import check_version


def make_repo(tmp_path, version="3.15.0", changelog="3.15.0", plugin="3.15.0"):
    (tmp_path / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{changelog}]: 2026-07-06\n\n- entry\n", encoding="utf-8")
    if plugin is not None:
        (tmp_path / ".claude-plugin").mkdir(exist_ok=True)
        (tmp_path / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "np", "version": plugin}), encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def _repo(**kwargs):
        make_repo(tmp_path, **kwargs)
        monkeypatch.setattr(check_version, "REPO_ROOT", tmp_path)
        return tmp_path
    return _repo


def run_main(argv=None):
    with pytest.raises(SystemExit) as exc:
        check_version.main(argv or [])
    return exc.value.code


def test_all_in_sync_passes(repo):
    repo()
    assert run_main() == 0


def test_changelog_mismatch_fails(repo):
    repo(changelog="3.14.9")
    assert run_main() == 1


def test_plugin_mismatch_fails(repo):
    repo(plugin="3.14.9")
    assert run_main() == 1


def test_missing_plugin_is_tolerated(repo):
    repo(plugin=None)
    assert run_main() == 0


def test_missing_changelog_heading_is_tolerated(repo, tmp_path):
    repo()
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\nno heading yet\n", encoding="utf-8")
    assert run_main() == 0


@pytest.mark.parametrize("files, ok", [
    (["scripts/x.py", "changes/feature-x.md"], True),       # feature PR with fragment
    (["VERSION", "CHANGELOG.md", "changes/a.md"], True),    # release PR
    (["scripts/x.py"], False),                              # no fragment
    (["scripts/x.py", "changes/README.md"], False),         # README is not a fragment
    ([], True),                                             # empty diff
])
def test_fragment_rule(files, ok):
    assert (check_version.fragment_problem(files) == "") is ok


def test_require_fragment_fails_without_one(repo, monkeypatch):
    repo()
    monkeypatch.setattr(check_version, "changed_files", lambda base: ["scripts/x.py"])
    assert run_main(["--require-fragment", "origin/main"]) == 1
