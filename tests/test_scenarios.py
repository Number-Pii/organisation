"""Tests for the scenario eval harness: definitions, scoring helpers, parsers.

No model is called here; live runs go through scripts/run_scenarios.py.
"""

import json
import subprocess
from pathlib import Path

import pytest

import run_scenarios as rs
from lib import agents

REPO_ROOT = Path(__file__).resolve().parent.parent


# ── scenario definitions ─────────────────────────────────────────────────────

SCENARIOS = rs.load_scenarios()


def test_every_brief_case_has_a_scenario():
    assert len(SCENARIOS) >= 12
    assert {"issue_feature", "unfamiliar_area", "bug_fix", "new_component",
            "architecture_change", "run_validation", "prepare_pr", "handover",
            "parallel_a", "parallel_b", "continue_work", "doc_discovery"} <= set(SCENARIOS)


@pytest.mark.parametrize("sid", sorted(SCENARIOS))
def test_scenario_is_well_formed(sid):
    scen = SCENARIOS[sid]
    assert scen["title"] and scen["prompt"].strip()
    if scen.get("pair"):
        assert SCENARIOS[scen["pair"]].get("pair_only")
    if scen["setup"]:
        assert (rs.SCEN_DIR / "overlays" / scen["setup"]["overlay"]).is_dir()
    for doc in scen["expect"].get("docs_read", []):
        assert (rs.FIXTURE / doc).is_file(), doc
    if scen["expect"].get("tests") and sid not in {"prepare_pr"}:
        assert (rs.SCEN_DIR / "hidden" / sid).is_dir(), f"{sid} has no hidden tests"


def test_smoke_set_excludes_pair_only():
    chosen = rs.select(SCENARIOS, [], smoke=True, everything=False)
    assert "parallel_a" in chosen and "parallel_b" not in chosen


def test_fixture_tests_pass_as_shipped():
    assert rs.run_tests(rs.FIXTURE, rs.FIXTURE / "tests", rs.FIXTURE)


# ── scoring helpers ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("path, patterns, ok", [
    ("doc/handover/engineering/handover-notes.md", ["doc/handover/**"], True),
    ("doc/handover/STATE.md", ["doc/handover/*/handover-notes.md"], False),
    ("tests/test_x.py", ["tests/**"], True),
    ("bookings/service.py", ["bookings/*.py"], True),
    ("bookings/sub/x.py", ["bookings/*.py"], False),
    ("README.md", [], False),
])
def test_glob_match(path, patterns, ok):
    assert rs.glob_match(path, patterns) is ok


def test_dash_churn_counts_punctuation_only_rewrites():
    patch = "\n".join([
        "--- a/x.md", "+++ b/x.md",
        "-This has changes — APIs may differ.",
        "+This has changes: APIs may differ.",
        "-A real edit — here.",
        "+A different sentence entirely.",
    ])
    assert rs.dash_churn(patch) == 1


def test_reads_before_first_edit_stops_at_edit():
    events = [agents.Event("read", "a.md"), agents.Event("shell", cmd="ls"),
              agents.Event("read", "a.md"), agents.Event("read", "b.md"),
              agents.Event("edit", "c.py"), agents.Event("read", "d.md")]
    assert rs.reads_before_first_edit(events) == ["a.md", "b.md"]


# ── runner parsing ───────────────────────────────────────────────────────────

def test_parse_claude_stream(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    lines = [
        {"type": "system", "subtype": "init", "model": "m1"},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": str(tmp_path / "a.txt")}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "cat a.txt && python3 -m unittest"}},
            {"type": "tool_use", "name": "Edit", "input": {"file_path": str(tmp_path / "a.txt")}}]}},
        {"type": "result", "result": "done", "num_turns": 3, "total_cost_usd": 0.1, "usage": {"x": 1}},
    ]
    result = agents.parse("claude", "\n".join(json.dumps(l) for l in lines), tmp_path)
    assert [(e.kind, e.path) for e in result.events] == [
        ("read", "a.txt"), ("shell", None), ("read", "a.txt"), ("edit", "a.txt")]
    assert (result.final_text, result.turns, result.model) == ("done", 3, "m1")


def test_parse_codex_stream(tmp_path):
    (tmp_path / "doc").mkdir()
    (tmp_path / "doc" / "spec.md").write_text("x")
    lines = [
        {"type": "item.completed", "item": {"type": "command_execution",
                                             "command": "/bin/zsh -lc \"sed -n '1,80p' doc/spec.md\""}},
        {"type": "item.completed", "item": {"type": "file_change",
                                             "changes": [{"path": str(tmp_path / "x.py"), "kind": "add"}]}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "finished"}},
        {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}},
    ]
    result = agents.parse("codex", "\n".join(json.dumps(l) for l in lines), tmp_path)
    assert [(e.kind, e.path) for e in result.events] == [
        ("shell", None), ("read", "doc/spec.md"), ("edit", "x.py")]
    assert result.final_text == "finished"
    assert result.usage == {"input_tokens": 10, "output_tokens": 2}


def test_codex_command_keeps_sandbox_and_scopes_git(tmp_path):
    work = tmp_path / "work"
    cmd = agents.command("codex", work, "hi", writable=(tmp_path,))
    assert "workspace-write" in cmd and "--dangerously-bypass-approvals-and-sandbox" not in cmd
    assert str(work / ".git") in cmd and str(tmp_path) in cmd
    assert agents.command("codex", work, "hi").count("--add-dir") == 1


def test_claude_command_never_skips_permissions(tmp_path):
    cmd = agents.command("claude", tmp_path, "hi")
    assert "acceptEdits" in cmd and not any("dangerously" in c for c in cmd)


# ── workspace build (no agent) ───────────────────────────────────────────────

def test_workspace_protects_main_and_seeds_handover(tmp_path):
    base = tmp_path / "base"
    rs.build_base("WORKTREE", base)
    work, preexisting, base_commit, _ = rs.prepare(base, tmp_path / "run", SCENARIOS["continue_work"])
    assert preexisting == ["feature/export-csv"]
    assert rs.git(work, "branch", "--show-current") == "main"
    assert (work / "organisation" / "scripts" / "init_project.py").is_file()
    assert "organisation" not in rs.git(work, "ls-files")
    (work / "README.md").write_text("changed\n")
    rs.commit_all(work, "direct to main")
    push = subprocess.run(["git", "-C", str(work), "push", "origin", "main"], capture_output=True)
    assert push.returncode != 0
    assert (tmp_path / "run" / "origin.git" / "rejected.log").read_text().strip() == "refs/heads/main"


def test_pair_merge_detects_shared_handover_conflict(tmp_path):
    """Two agents from one base: disjoint code merges cleanly, a shared handover line does not."""
    base = tmp_path / "base"
    rs.build_base("WORKTREE", base)
    a, b = tmp_path / "a" / "run", tmp_path / "b" / "run"
    for run_dir in (a, b):
        rs.clone_base(base, run_dir)
    base_commit = rs.git(base / "work", "rev-parse", "main")
    rs.git(a / "work", "worktree", "add", "-q", "-b", "fix/x", str(a / "wt"))  # A uses a worktree
    (a / "wt" / "bookings" / "a.py").write_text("x = 1\n")
    rs.commit_all(a / "wt", "a")
    rs.git(b / "work", "checkout", "-q", "-b", "feature/y")
    (b / "work" / "bookings" / "b.py").write_text("y = 1\n")
    rs.commit_all(b / "work", "b")
    assert rs.merge_conflicts(a, b, base_commit)["merged"] is True

    shared = "doc/shared.md"
    for tree, name in ((a / "wt", "A"), (b / "work", "B")):
        (tree / shared).write_text(f"entry {name}\n")
        rs.commit_all(tree, "shared")
    outcome = rs.merge_conflicts(a, b, base_commit)
    assert outcome["merged"] is False and outcome["conflicted_files"] == [shared]
