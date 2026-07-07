"""Tests for orchestration v2: Status field control, claim lock, board write-back."""

from gh_project_sync import (
    find_project_item,
    find_status_field,
    reassignment_needs_force,
    rewrite_board_states,
)

FIELDS = [
    {"id": "F0", "name": "Title", "type": "ProjectV2Field"},
    {"id": "F7", "name": "Status", "type": "ProjectV2SingleSelectField",
     "options": [
         {"id": "O1", "name": "Backlog"},
         {"id": "O2", "name": "In Progress"},
         {"id": "O3", "name": "Completed"},
     ]},
]

ITEMS = [
    {"id": "I1", "status": "In Progress",
     "content": {"number": 42, "repository": "Number-Pii/fixture", "title": "Set up schema"}},
    {"id": "I2", "status": "Backlog",
     "content": {"number": 43, "repository": "Number-Pii/fixture", "title": "JWT middleware"}},
    {"id": "I3", "status": "Backlog", "content": None},
]


def test_find_status_field_returns_id_and_options():
    field_id, options = find_status_field(FIELDS)
    assert field_id == "F7"
    assert options == {"backlog": "O1", "in progress": "O2", "completed": "O3"}


def test_find_status_field_missing():
    assert find_status_field([{"id": "F0", "name": "Title"}]) == ("", {})


def test_find_project_item_matches_repo_and_number():
    assert find_project_item(ITEMS, "Number-Pii/fixture", 42)["id"] == "I1"
    assert find_project_item(ITEMS, "number-pii/FIXTURE", 43)["id"] == "I2"
    assert find_project_item(ITEMS, "Number-Pii/other", 42) == {}
    assert find_project_item(ITEMS, "Number-Pii/fixture", 99) == {}


def test_reassignment_needs_force_only_for_claimed_items():
    assert reassignment_needs_force(["alice"], "bob", "In Progress")
    assert reassignment_needs_force(["alice"], "bob", "in progress")
    assert not reassignment_needs_force(["alice"], "bob", "Ready")
    assert not reassignment_needs_force(["alice"], "alice", "In Progress")
    assert not reassignment_needs_force([], "bob", "In Progress")
    assert not reassignment_needs_force(["alice"], "", "In Progress")


BOARD = """# Task Board: Fixture

## Backlog
<!-- Example rows that must never be rewritten:
     | 99 | Set up schema | backend | p0 | X | human | Backlog | none |
-->

| ID | Title | Area | Priority | Owner | Owner Type | State | Depends On |
|----|-------|------|----------|-------|------------|-------|------------|
| 1 | Set up schema | backend | p1 | Lead | human | Ready | none |
| 2 | JWT middleware | backend | p1 | @agent | agent | Backlog | 1 |

## Claiming Work
| Title | State |
|-------|-------|
| Set up schema | untouched-other-section |
"""


def test_rewrite_updates_state_cells():
    new, updated, unmatched = rewrite_board_states(
        BOARD, {"Set up schema": "In Progress", "JWT middleware": "Backlog"})
    assert updated == ["Set up schema"]
    assert unmatched == []
    assert "| 1 | Set up schema | backend | p1 | Lead | human | In Progress | none |" in new
    # unchanged row keeps its original formatting
    assert "| 2 | JWT middleware | backend | p1 | @agent | agent | Backlog | 1 |" in new


def test_rewrite_reports_unmatched_titles():
    new, updated, unmatched = rewrite_board_states(BOARD, {"Set up schema": "Review"})
    assert updated == ["Set up schema"]
    assert unmatched == ["JWT middleware"]


def test_rewrite_never_touches_comments_or_other_sections():
    new, _, _ = rewrite_board_states(BOARD, {"Set up schema": "Completed"})
    assert "| 99 | Set up schema | backend | p0 | X | human | Backlog | none |" in new
    assert "untouched-other-section" in new


def test_rewrite_noop_when_states_match():
    new, updated, unmatched = rewrite_board_states(
        BOARD, {"Set up schema": "Ready", "JWT middleware": "Backlog"})
    assert new == BOARD
    assert updated == []
