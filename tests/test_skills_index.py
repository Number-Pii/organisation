"""Tests for build_skills_index.py generation and find_skill.py filtering."""

from pathlib import Path

import pytest

import build_skills_index as bsi
from find_skill import filter_skills, matches


def make_library(tmp_path: Path) -> Path:
    skills = tmp_path / "Teams" / "skills"
    cases = {
        "alpha-db": {"tier": "curated", "canonical": "true", "domain": "Backend",
                     "summary": "Design database schemas."},
        "beta-db": {"tier": "", "canonical": "", "domain": "Backend",
                    "summary": "Another database helper."},
        "old-persona": {"tier": "archive", "canonical": "", "domain": "Personas",
                        "summary": "Celebrity persona."},
    }
    for name, fm in cases.items():
        folder = skills / name
        folder.mkdir(parents=True)
        lines = ["---", f"name: {name}", "risk: low"]
        if fm["tier"]:
            lines.append(f"tier: {fm['tier']}")
        if fm["canonical"]:
            lines.append(f"canonical: {fm['canonical']}")
        lines += [f'domain: "{fm["domain"]}"', "size_class: xs",
                  f'summary: "{fm["summary"]}"', "detail_sections:", "  - Usage", "---", "", "# body"]
        (folder / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return skills


@pytest.fixture
def library(tmp_path, monkeypatch):
    skills = make_library(tmp_path)
    monkeypatch.setattr(bsi, "SKILLS_DIR", skills)
    monkeypatch.setattr(bsi, "INDEX_PATH", skills / "skills-index.json")
    monkeypatch.setattr(bsi, "CATEGORIES_PATH", skills / "CATEGORIES.md")
    return skills


def test_collect_skills_defaults_tier_to_standard(library):
    skills = bsi.collect_skills()
    by_name = {s["name"]: s for s in skills}
    assert by_name["beta-db"]["tier"] == "standard"
    assert by_name["alpha-db"]["tier"] == "curated"
    assert by_name["alpha-db"]["canonical"] is True


def test_categories_lists_archive_separately(library):
    text = bsi.render_categories(bsi.collect_skills())
    assert "## Archived" in text
    archived_part = text.split("## Archived")[1]
    assert "`old-persona`" in archived_part
    assert "old-persona" not in text.split("## Archived")[0]
    assert "`alpha-db` (canonical)" in text


def test_check_mode_detects_drift(library, capsys):
    bsi.INDEX_PATH.write_text("{}", encoding="utf-8")
    bsi.CATEGORIES_PATH.write_text("stale", encoding="utf-8")
    import sys
    argv = sys.argv
    sys.argv = ["build_skills_index.py", "--check"]
    try:
        assert bsi.main() == 1
        bsi.INDEX_PATH.write_text(bsi.render_index(bsi.collect_skills()), encoding="utf-8")
        bsi.CATEGORIES_PATH.write_text(bsi.render_categories(bsi.collect_skills()), encoding="utf-8")
        assert bsi.main() == 0
    finally:
        sys.argv = argv


INDEX = [
    {"name": "alpha-db", "domain": "Backend", "summary": "Design database schemas.",
     "tier": "curated", "canonical": True},
    {"name": "beta-db", "domain": "Backend", "summary": "Another database helper.",
     "tier": "standard", "canonical": False},
    {"name": "old-persona", "domain": "Personas", "summary": "Celebrity persona.",
     "tier": "archive", "canonical": False},
]


def test_matches_searches_summaries_not_just_names():
    assert matches(INDEX[0], "schemas")
    assert matches(INDEX[0], "alpha")
    assert not matches(INDEX[0], "persona")


def test_default_tier_hides_standard_and_archive():
    visible, hidden = filter_skills(INDEX, "db", None, {"curated"})
    assert [s["name"] for s in visible] == ["alpha-db"]
    assert hidden == 1


def test_all_tiers_rank_canonical_then_tier():
    visible, hidden = filter_skills(INDEX, None, None, {"curated", "standard", "archive"})
    assert [s["name"] for s in visible] == ["alpha-db", "beta-db", "old-persona"]
    assert hidden == 0


def test_domain_filter_is_partial_match():
    visible, _ = filter_skills(INDEX, None, "back", {"curated", "standard", "archive"})
    assert {s["name"] for s in visible} == {"alpha-db", "beta-db"}
