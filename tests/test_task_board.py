"""Fixture tests for the task-board parsing in scripts/gh_project_sync.py."""

import pytest

from gh_project_sync import _parse_markdown_table, _section_lines, parse_board, require_config

BOARD = """# Task Board: Fixture

## Board Configuration
<!-- guidance comment -->

| Setting | Value |
|---------|-------|
| GitHub Project number | 7 |
| Project owner | Number-Pii |
| Repository | Number-Pii/fixture |

## Backlog
<!-- Example rows that must never be parsed:
     | 99 | Ghost task | backend | p0 | Nobody | human | Ready | none |
-->

| ID | Title | Area | Priority | Owner | Owner Type | State | Depends On |
|----|-------|------|----------|-------|------------|-------|------------|
| 1 | Set up schema | backend | p1 | Lead Backend Engineer | human | Ready | none |
| 2 | JWT middleware | backend | p1 | @backend-dev-guidelines | agent | Backlog | 1 |
"""


def test_parse_markdown_table_rows_keyed_by_lowercased_header():
    lines = [
        "| Name | Role |",
        "|------|------|",
        "| Ada | Engineer |",
    ]
    rows = _parse_markdown_table(lines)
    assert rows == [{"name": "Ada", "role": "Engineer"}]


def test_parse_markdown_table_pads_short_rows():
    lines = [
        "| A | B | C |",
        "|---|---|---|",
        "| 1 | 2 |",
    ]
    assert _parse_markdown_table(lines) == [{"a": "1", "b": "2", "c": ""}]


def test_parse_markdown_table_stops_at_first_gap_after_table():
    lines = [
        "| A |",
        "|---|",
        "| 1 |",
        "",
        "| 2 |",
    ]
    assert _parse_markdown_table(lines) == [{"a": "1"}]


def test_parse_markdown_table_handles_no_table():
    assert _parse_markdown_table(["no table here", ""]) == []


def test_section_lines_extracts_between_h2_headings():
    text = "## One\na\n## Two\nb\nc\n## Three\nd\n"
    assert _section_lines(text, "Two") == ["b", "c"]
    assert _section_lines(text, "missing") == []


def test_parse_board_reads_config_and_backlog(tmp_path):
    board = tmp_path / "task-board.md"
    board.write_text(BOARD, encoding="utf-8")
    config, tasks = parse_board(board)
    assert config == {
        "project_number": "7",
        "project_owner": "Number-Pii",
        "repository": "Number-Pii/fixture",
    }
    assert [t["title"] for t in tasks] == ["Set up schema", "JWT middleware"]
    assert tasks[1]["owner type"] == "agent"


def test_parse_board_ignores_commented_example_rows(tmp_path):
    board = tmp_path / "task-board.md"
    board.write_text(BOARD, encoding="utf-8")
    _, tasks = parse_board(board)
    assert all(t["title"] != "Ghost task" for t in tasks)


def test_parse_board_treats_todo_config_as_missing(tmp_path):
    board = tmp_path / "task-board.md"
    board.write_text(
        BOARD.replace("| GitHub Project number | 7 |",
                      "| GitHub Project number | TODO |"),
        encoding="utf-8",
    )
    config, _ = parse_board(board)
    assert config["project_number"] == ""
    with pytest.raises(SystemExit):
        require_config(config, "project_number")


def test_parse_board_missing_file_escalates(tmp_path):
    with pytest.raises(SystemExit):
        parse_board(tmp_path / "absent.md")


def test_require_config_passes_when_complete():
    require_config({"repository": "o/r"}, "repository")  # must not raise
