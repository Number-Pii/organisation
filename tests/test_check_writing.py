"""Unit tests for scripts/check_writing.py."""

from pathlib import Path

from check_writing import (
    check_file,
    load_banned_phrases,
    phrase_pattern,
    prose_sentences,
    scannable_lines,
)

BANNED = ["leverage", "deep dive", "in order to"]
TARGET = (30.0, 40.0)


def write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "doc.md"
    p.write_text(text, encoding="utf-8")
    return p


def run(tmp_path, text):
    return check_file(write(tmp_path, text), BANNED, TARGET)


def test_em_dash_fails(tmp_path):
    fails, _, _ = run(tmp_path, "A sentence — with an em dash.\n")
    assert any("Em dash" in f for f in fails)


def test_en_dash_fails(tmp_path):
    fails, _, _ = run(tmp_path, "Pages 3–7 cover setup.\n")
    assert any("En dash" in f for f in fails)


def test_dash_rule_mention_is_exempt(tmp_path):
    fails, _, _ = run(tmp_path, "No em dashes (—) and no en dashes (–) anywhere.\n")
    assert fails == []


def test_banned_phrase_fails_case_insensitively(tmp_path):
    fails, _, _ = run(tmp_path, "We will Leverage the platform.\n")
    assert any('Banned phrase "leverage"' in f for f in fails)


def test_banned_phrase_matches_across_whitespace(tmp_path):
    fails, _, _ = run(tmp_path, "Take a deep  dive into the data.\n")
    assert any("deep dive" in f for f in fails)


def test_code_blocks_and_comments_are_skipped(tmp_path):
    text = (
        "Real prose sits here.\n\n"
        "```\nleverage — inside a fence\n```\n\n"
        "<!-- leverage — inside a comment -->\n"
        "And `leverage` inline code is fine.\n"
    )
    fails, _, _ = run(tmp_path, text)
    assert fails == []


def test_three_identical_openers_fail(tmp_path):
    text = (
        "The system runs nightly.\n\n"
        "The report lands at nine.\n\n"
        "The team reads it after standup.\n"
    )
    fails, _, _ = run(tmp_path, text)
    assert any("Three consecutive sentences" in f for f in fails)


def test_clean_prose_passes(tmp_path):
    text = (
        "# Fixture\n\n"
        "Reviews happen before merge.\n\n"
        "A second reader checks the risky parts.\n\n"
        "Nothing ships without both.\n"
    )
    fails, _, _ = run(tmp_path, text)
    assert fails == []


def test_scannable_lines_keeps_line_numbers(tmp_path):
    lines = scannable_lines("one\n```\nskip\n```\nfive\n")
    assert [n for n, _ in lines] == [1, 5]


def test_prose_sentences_excludes_headings_and_tables():
    lines = [(1, "# Heading"), (2, "| a | b |"), (3, "A real sentence here.")]
    assert prose_sentences(lines) == ["A real sentence here."]


def test_phrase_pattern_word_boundaries():
    pat = phrase_pattern("leverage")
    assert pat.search("we leverage this")
    assert not pat.search("cleverageous")


def test_load_banned_phrases_reads_writing_md():
    phrases = load_banned_phrases()
    assert "delve" in phrases
    assert len(phrases) > 30
