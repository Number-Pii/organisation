"""Running the toolkit must not modify files whose content has not changed.

Covers the two churn paths found in the 2026-09 review: generators rewriting
unchanged outputs, and scaffolded context files carrying a render date.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from init_project import build_files
from lib.files import write_if_changed

REPO_ROOT = Path(__file__).resolve().parent.parent

GENERATORS = {
    "build_agents.py": sorted((REPO_ROOT / "agents").glob("np-*.md")),
    "build_org.py": [REPO_ROOT / "Teams" / "org.json"],
    "build_skills_index.py": [REPO_ROOT / "Teams" / "skills" / "skills-index.json",
                              REPO_ROOT / "Teams" / "skills" / "CATEGORIES.md"],
    "sync_ai_context.py": [REPO_ROOT / "AGENTS.md", REPO_ROOT / "GEMINI.md"],
}


@pytest.mark.parametrize("script", sorted(GENERATORS))
def test_generator_leaves_current_outputs_untouched(script):
    outputs = GENERATORS[script]
    assert outputs, f"{script} has no outputs to check"
    before = {p: p.stat().st_mtime_ns for p in outputs}
    result = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / script)],
                            capture_output=True, text=True, cwd=REPO_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    after = {p: p.stat().st_mtime_ns for p in outputs}
    assert before == after, f"{script} rewrote unchanged files"


def test_write_if_changed(tmp_path):
    path = tmp_path / "x.md"
    assert write_if_changed(path, "a\n") is True
    mtime = path.stat().st_mtime_ns
    assert write_if_changed(path, "a\n") is False
    assert path.stat().st_mtime_ns == mtime
    assert write_if_changed(path, "b\n") is True


def test_context_files_do_not_depend_on_render_date():
    """Re-rendering the root context files on another day must give identical bytes."""
    kwargs = dict(project_name="Churn", departments=["engineering"], output_dir=Path("."), level=2)
    monday = build_files(today="2026-09-21", **kwargs)
    friday = build_files(today="2026-09-25", **kwargs)
    for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
        path = Path(name)
        assert monday[path] == friday[path], f"{name} changes with the render date"
