"""Fixture tests for the shared frontmatter parser (scripts/lib/frontmatter.py)."""

from pathlib import Path

import pytest

from lib.frontmatter import parse_frontmatter, size_class_for


def write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "SKILL.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_flat_scalars_and_quotes(tmp_path):
    p = write(tmp_path, "---\nname: postgres\nsummary: \"Design schemas\"\nrisk: 'low'\n---\nbody\n")
    fm, total = parse_frontmatter(p)
    assert fm == {"name": "postgres", "summary": "Design schemas", "risk": "low"}
    assert total == 6


def test_flow_sequence(tmp_path):
    p = write(tmp_path, "---\ntags: [a, \"b\", c d]\n---\n")
    fm, _ = parse_frontmatter(p)
    assert fm["tags"] == ["a", "b", "c d"]


def test_block_list(tmp_path):
    p = write(tmp_path, "---\ndetail_sections:\n  - Setup\n  - Usage\n---\n")
    fm, _ = parse_frontmatter(p)
    assert fm["detail_sections"] == ["Setup", "Usage"]


def test_comments_and_blank_lines_skipped(tmp_path):
    p = write(tmp_path, "---\n# a comment\nname: x\n\nrisk: low\n---\n")
    fm, _ = parse_frontmatter(p)
    assert fm == {"name": "x", "risk": "low"}


def test_no_frontmatter_returns_empty_dict(tmp_path):
    p = write(tmp_path, "# Just a heading\n\nBody text.\n")
    fm, total = parse_frontmatter(p)
    assert fm == {}
    assert total == 3


def test_unterminated_frontmatter_degrades_to_empty(tmp_path):
    p = write(tmp_path, "---\nname: x\nno closing fence\n")
    fm, total = parse_frontmatter(p)
    assert fm == {}
    assert total == 3


def test_empty_file(tmp_path):
    p = write(tmp_path, "")
    assert parse_frontmatter(p) == ({}, 0)


def test_missing_file_returns_empty(tmp_path):
    assert parse_frontmatter(tmp_path / "absent.md") == ({}, 0)


def test_undecodable_file_returns_empty(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_bytes(b"\xff\xfe\x00 not utf-8 \x9c")
    assert parse_frontmatter(p) == ({}, 0)


def test_malformed_key_lines_are_ignored(tmp_path):
    p = write(tmp_path, "---\nname: x\njust some words without a colon\n---\n")
    fm, _ = parse_frontmatter(p)
    assert fm == {"name": "x"}


@pytest.mark.parametrize(
    "count,expected",
    [(0, "xs"), (49, "xs"), (50, "s"), (199, "s"), (200, "m"),
     (499, "m"), (500, "l"), (999, "l"), (1000, "xl"), (5000, "xl")],
)
def test_size_class_bands(count, expected):
    assert size_class_for(count) == expected
