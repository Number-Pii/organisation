"""Tests for scripts/release.py: changelog fragments compile into one release."""

import json

import pytest

import release


def make_repo(tmp_path, version="3.19.1"):
    (tmp_path / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\nPreamble.\n\n---\n\n## [3.19.1]: 2026-07-07\n\n- old\n",
        encoding="utf-8")
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "np", "version": version}, indent=2) + "\n", encoding="utf-8")
    (tmp_path / "changes").mkdir()
    (tmp_path / "changes" / "README.md").write_text("# not a fragment\n", encoding="utf-8")
    return tmp_path


def fragment(root, name, text):
    (root / "changes" / name).write_text(text, encoding="utf-8")


def test_highest_bump_wins_and_sections_merge(tmp_path):
    root = make_repo(tmp_path)
    fragment(root, "fix-a.md", "---\nbump: patch\nsection: Fixed\n---\n- Fixed A.\n")
    fragment(root, "feature-b.md",
             "---\nbump: minor   # comment\nsection: Added\n---\n- Added B.\n\n"
             "### Fixed\n- Fixed B.\n")
    current, new, files, section = release.build_release(root, None, "2026-09-23")
    assert (current, new) == ("3.19.1", "3.20.0")
    assert len(files) == 2
    assert section.index("### Added") < section.index("### Fixed")
    assert "- Added B." in section and "- Fixed A." in section and "- Fixed B." in section


def test_write_release_updates_all_three_and_removes_fragments(tmp_path):
    root = make_repo(tmp_path)
    fragment(root, "feature-b.md", "---\nbump: major\n---\n- Big change.\n")
    _, new, files, section = release.build_release(root, None, "2026-09-23")
    release.write_release(root, new, files, section)
    assert (root / "VERSION").read_text().strip() == "4.0.0"
    assert json.loads((root / ".claude-plugin" / "plugin.json").read_text())["version"] == "4.0.0"
    changelog = (root / "CHANGELOG.md").read_text()
    assert changelog.index("## [4.0.0]: 2026-09-23") < changelog.index("## [3.19.1]")
    assert changelog.startswith("# Changelog\n\nPreamble.")
    assert "### Changed\n- Big change." in changelog
    assert sorted(p.name for p in (root / "changes").iterdir()) == ["README.md"]


def test_no_fragments_is_an_error(tmp_path):
    root = make_repo(tmp_path)
    with pytest.raises(ValueError):
        release.build_release(root, None, "2026-09-23")


def test_bad_bump_is_an_error(tmp_path):
    root = make_repo(tmp_path)
    fragment(root, "x.md", "---\nbump: huge\n---\n- x\n")
    with pytest.raises(ValueError):
        release.build_release(root, None, "2026-09-23")


def test_explicit_version_overrides(tmp_path):
    root = make_repo(tmp_path)
    fragment(root, "x.md", "- plain bullet, no frontmatter\n")
    _, new, _, section = release.build_release(root, "3.19.5", "2026-09-23")
    assert new == "3.19.5"
    assert "### Changed\n- plain bullet" in section
