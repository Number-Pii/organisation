"""Golden-file and behaviour tests for scripts/init_project.py."""

import subprocess
import sys
from pathlib import Path

import pytest

from init_project import LEVELS, build_files, scaffold
from generate_goldens import GOLDEN_CASES, GOLDEN_PROJECT_NAME, GOLDEN_TODAY, build_case

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
GOLDEN_DIR = TESTS_DIR / "golden"


@pytest.mark.parametrize("case", sorted(GOLDEN_CASES))
def test_scaffold_matches_golden(case):
    """Rendered output is byte-identical to the reviewed golden tree."""
    built = build_case(GOLDEN_CASES[case], Path("."))
    built_by_rel = {str(path): content for path, content in built.items()}

    case_dir = GOLDEN_DIR / case
    golden_files = {
        str(p.relative_to(case_dir)): p.read_text(encoding="utf-8")
        for p in case_dir.rglob("*.md")
    }

    assert set(built_by_rel) == set(golden_files), (
        "file set drifted; if intentional run tests/generate_goldens.py and review the diff"
    )
    for rel, content in golden_files.items():
        assert built_by_rel[rel] == content, (
            f"{case}/{rel} drifted from golden; if intentional run "
            "tests/generate_goldens.py and review the diff"
        )


@pytest.mark.parametrize("level", [1, 2, 3, 4])
def test_no_unrendered_placeholders(level):
    built = build_files(
        project_name="Placeholder Check", departments=["engineering"],
        output_dir=Path("."), level=level, existing=True, today="2026-01-01",
    )
    for path, content in built.items():
        assert "$" not in content, f"unrendered placeholder in {path}"


def test_architecture_only_at_level_3_plus():
    for level, expected in [(1, False), (2, False), (3, True), (4, True)]:
        built = build_files(
            project_name="X", departments=["engineering"],
            output_dir=Path("."), level=level, today="2026-01-01",
        )
        names = {p.name for p in built}
        assert ("architecture.md" in names) is expected, f"level {level}"


def test_codebase_assessment_only_when_existing():
    kwargs = dict(project_name="X", departments=["engineering"],
                  output_dir=Path("."), level=2, today="2026-01-01")
    greenfield = {p.name for p in build_files(**kwargs)}
    brownfield = {p.name for p in build_files(existing=True, **kwargs)}
    assert "codebase-assessment.md" not in greenfield
    assert "codebase-assessment.md" in brownfield


@pytest.mark.parametrize("level", [1, 2, 3, 4])
def test_version_control_carries_level_pr_rules(level):
    built = build_files(
        project_name="X", departments=["engineering"],
        output_dir=Path("."), level=level, today="2026-01-01",
    )
    vc = built[Path(".") / "doc" / "version_control.md"]
    for rule in LEVELS[level]["pr_rules"]:
        assert rule in vc, f"level {level} missing PR rule: {rule}"
    assert LEVELS[level]["release_process"] in vc


def test_level4_pr_rules_demand_two_reviews_and_cto_signoff():
    """Level 4's own definition requires two reviewers and CTO sign-off; the
    scaffolded contract must say so rather than default to one review."""
    built = build_files(
        project_name="X", departments=["engineering"],
        output_dir=Path("."), level=4, today="2026-01-01",
    )
    vc = built[Path(".") / "doc" / "version_control.md"]
    assert "Two approving reviews" in vc
    assert "CTO-level sign-off" in vc
    assert "At least 1 peer review" not in vc


def test_department_folders_slugified():
    built = build_files(
        project_name="X", departments=["Growth Marketing"],
        output_dir=Path("."), level=1, today="2026-01-01",
    )
    rels = {str(p) for p in built}
    assert "doc/handover/growth-marketing/handover-notes.md" in rels


def test_scaffold_never_overwrites(tmp_path, capsys):
    scaffold("X", ["engineering"], tmp_path, dry_run=False, level=1)
    brief = tmp_path / "doc" / "project-brief.md"
    brief.write_text("user edits", encoding="utf-8")
    scaffold("X", ["engineering"], tmp_path, dry_run=False, level=1)
    assert brief.read_text(encoding="utf-8") == "user edits"
    assert "[SKIP]" in capsys.readouterr().out


def test_dry_run_creates_nothing(tmp_path):
    scaffold("X", ["engineering"], tmp_path, dry_run=True, level=2)
    assert list(tmp_path.iterdir()) == []


def test_refuses_toolkit_root_as_output_dir():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "init_project.py"),
         "--project-name", "X", "--output-dir", str(REPO_ROOT), "--dry-run"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "toolkit itself" in result.stdout


def test_missing_template_fails_loudly(monkeypatch, tmp_path):
    import init_project
    monkeypatch.setattr(init_project, "TEMPLATES_DIR", tmp_path / "absent")
    with pytest.raises(SystemExit):
        build_files("X", ["engineering"], Path("."), level=1, today="2026-01-01")


def test_golden_project_name_renders_into_every_file():
    built = build_case(GOLDEN_CASES["level2"], Path("."))
    for path, content in built.items():
        assert GOLDEN_PROJECT_NAME in content, f"{path} missing project name"
        assert GOLDEN_TODAY in content or "archive" in str(path), path
