"""Tests for scripts/sync_context.py: the managed block and nothing else."""

import os
from pathlib import Path

import pytest

import sync_context

NEXT = ("<!-- BEGIN:nextjs-agent-rules -->\nBreaking changes — read the docs.\n"
        "<!-- END:nextjs-agent-rules -->\n")


@pytest.fixture
def cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_refresh_replaces_only_the_block(cwd):
    agents = write(cwd / "AGENTS.md",
                   "# Project\n\nOur own words — kept.\n\n<!-- np:begin -->\nSTALE-BLOCK\n<!-- np:end -->\n\n" + NEXT)
    assert sync_context.main([]) == 0
    text = agents.read_text()
    assert text.startswith("# Project\n\nOur own words — kept.\n\n<!-- np:begin -->")
    assert text.endswith(NEXT)
    assert "STALE-BLOCK" not in text and "## How work is done here" in text


def test_second_run_writes_nothing(cwd):
    agents = write(cwd / "AGENTS.md", "# P\n\n<!-- np:begin -->\nSTALE-BLOCK\n<!-- np:end -->\n")
    sync_context.main([])
    os.utime(agents, (1, 1))
    assert sync_context.main([]) == 0
    assert agents.stat().st_mtime == 1
    assert sync_context.main(["--check"]) == 0


def test_unmarked_file_is_refused_unless_appending(cwd):
    original = "# Hand-written context — precious.\n\nKeep every line.\n"
    agents = write(cwd / "AGENTS.md", original)
    assert sync_context.main([]) == 1
    assert agents.read_text() == original
    assert sync_context.main(["--append"]) == 0
    text = agents.read_text()
    assert text.startswith(original.rstrip("\n")) and text.count("<!-- np:begin -->") == 1


def test_check_reports_stale_block(cwd):
    write(cwd / "AGENTS.md", "# P\n\n<!-- np:begin -->\nSTALE-BLOCK\n<!-- np:end -->\n")
    assert sync_context.main(["--check"]) == 1


def test_two_blocks_are_an_error(cwd):
    write(cwd / "AGENTS.md", "<!-- np:begin -->\na\n<!-- np:end -->\n<!-- np:begin -->\nb\n<!-- np:end -->\n")
    assert sync_context.main([]) == 1
