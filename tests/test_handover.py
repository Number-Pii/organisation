"""Tests for scripts/handover.py: per-branch entries that never conflict."""

import subprocess
from pathlib import Path

import pytest

import handover
from init_project import scaffold

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


def run(repo: Path, *args: str) -> str:
    return subprocess.run([*GIT, "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def project(tmp_path, monkeypatch):
    scaffold("Demo", ["engineering"], tmp_path, dry_run=False, level=2)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    run(tmp_path, "add", "-A")
    run(tmp_path, "commit", "-qm", "chore: scaffold")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def new_entry(repo: Path, branch: str, date: str) -> Path:
    run(repo, "checkout", "-q", "-b", branch, "main")
    (repo / "app.py").write_text(f"# {branch}\n")
    run(repo, "add", "app.py")
    run(repo, "commit", "-qm", f"feat: work on {branch}")
    assert handover.main(["--project", str(repo), "new", "--date", date, "--base", "main"]) == 0
    path = repo / "doc" / "handover" / "entries" / f"{date}-{handover.slug(branch)}.md"
    run(repo, "add", "-A")
    run(repo, "commit", "-qm", "docs: handover")
    return path


def test_new_prefills_commits_and_refuses_main(project, capsys):
    entry = new_entry(project, "feature/login", "2026-09-23")
    text = entry.read_text()
    assert "branch: feature/login" in text and "- feat: work on feature/login" in text
    run(project, "checkout", "-q", "main")
    assert handover.main(["--project", str(project), "new"]) == 1


def test_parallel_branches_merge_without_conflicts(project):
    """The v3 layout conflicted in 2 of 3 measured parallel pairs; this must not."""
    new_entry(project, "feature/a", "2026-09-23")
    run(project, "checkout", "-q", "main")
    run(project, "checkout", "-q", "-b", "fix/b", "main")
    assert handover.main(["--project", str(project), "new", "--date", "2026-09-23",
                          "--base", "main"]) == 0
    run(project, "add", "-A")
    run(project, "commit", "-qm", "docs: handover b")
    run(project, "checkout", "-q", "main")
    run(project, "merge", "-q", "--no-edit", "feature/a")
    merged = subprocess.run([*GIT, "-C", str(project), "merge", "--no-edit", "fix/b"],
                            capture_output=True, text=True)
    assert merged.returncode == 0, merged.stdout + merged.stderr


@pytest.mark.parametrize("branch, files, fails, warns", [
    ("fix/b", ["app.py", "doc/handover/entries/2026-09-23-fix-b.md"], 0, 0),
    ("fix/b", ["doc/handover/entries/2026-09-23-feature-a.md"], 1, 0),
    ("fix/b", ["doc/handover/STATE.md"], 1, 0),
    ("fix/b", ["app.py"], 0, 1),
    ("fix/b", ["doc/specs/x.md"], 0, 0),
    ("chore/handover-consolidate-2026-09-30", ["doc/handover/STATE.md"], 0, 0),
])
def test_check_rules(branch, files, fails, warns):
    f, w = handover.classify(files, branch)
    assert (len(f), len(w)) == (fails, warns)


def test_consolidate_drafts_and_marks(project, capsys):
    entry = new_entry(project, "feature/a", "2026-09-23")
    entry.write_text(entry.read_text().replace(
        "[What this branch is for, and the issue or request it answers.]", "Add login."))
    run(project, "checkout", "-q", "-b", "chore/handover-consolidate-2026-09-30")
    assert handover.main(["--project", str(project), "consolidate", "--mark"]) == 0
    out = capsys.readouterr().out
    assert "Add login." in out
    state = (project / "doc" / "handover" / "STATE.md").read_text()
    assert "consolidated_through: 2026-09-23" in state


def test_status_points_legacy_projects_to_migration(tmp_path, capsys):
    legacy = tmp_path / "doc" / "handover"
    legacy.mkdir(parents=True)
    (legacy / "consolidated_handover.md").write_text("# old\n")
    assert handover.main(["--project", str(tmp_path), "status"]) == 0
    assert "migrate_consumer.py" in capsys.readouterr().out
