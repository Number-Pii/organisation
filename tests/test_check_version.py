"""Unit tests for scripts/check_version.py against a fixture repo tree."""

import pytest

import check_version


def make_repo(tmp_path, version="3.15.0", changelog="3.15.0",
              claude="2.14", gemini="2.14", agents="2.14"):
    (tmp_path / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{changelog}]: 2026-07-06\n\n- entry\n", encoding="utf-8")
    for name, ver in [("CLAUDE.md", claude), ("GEMINI.md", gemini), ("AGENTS.md", agents)]:
        (tmp_path / name).write_text(
            f"# Context\n\n_Version: {ver} | Last updated: 2026-07-06_\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def _repo(**kwargs):
        make_repo(tmp_path, **kwargs)
        monkeypatch.setattr(check_version, "REPO_ROOT", tmp_path)
        return tmp_path
    return _repo


def run_main():
    with pytest.raises(SystemExit) as exc:
        check_version.main()
    return exc.value.code


def test_all_in_sync_passes(repo):
    repo()
    assert run_main() == 0


def test_changelog_mismatch_fails(repo):
    repo(changelog="3.14.9")
    assert run_main() == 1


def test_gemini_drift_fails(repo):
    repo(gemini="2.13")
    assert run_main() == 1


def test_agents_drift_fails(repo):
    """The 3.14.2 fix: AGENTS.md drift must fail, not pass silently."""
    repo(agents="2.13")
    assert run_main() == 1


def test_missing_changelog_heading_is_tolerated(repo, tmp_path):
    repo()
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\nno heading yet\n", encoding="utf-8")
    assert run_main() == 0
