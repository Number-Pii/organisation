#!/usr/bin/env python3
"""
generate_skill_frontmatter.py — propose extended frontmatter for a SKILL.md.

The toolkit opts skills into lazy-loading by appending four fields to the
existing YAML frontmatter:

    domain:          one of the 17 canonical categories in CATEGORIES.md
    size_class:      xs | s | m | l | xl  (derived from line count)
    summary:         one-line "what's this skill for", ≤150 chars
    detail_sections: top-level ## headers a loader can expand on demand

This script reads a SKILL.md, computes proposed values, and prints the
resulting full frontmatter block to stdout. A human reviews the proposal
and pastes it back into the file.

Usage:
    python3 scripts/generate_skill_frontmatter.py Teams/skills/<name>/SKILL.md
    python3 scripts/generate_skill_frontmatter.py Teams/skills/<name>/SKILL.md --write
        # in-place replacement of the existing frontmatter block

The --write flag keeps every existing key and only appends the four new
fields (or overwrites them if they already exist).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_skills import parse_frontmatter, size_class_for  # noqa: E402

REPO_ROOT = HERE.parent
CATEGORIES_MD = REPO_ROOT / "Teams" / "skills" / "CATEGORIES.md"
SKILL_TOKEN = re.compile(r"`([a-z0-9][a-z0-9\-]*)`")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
SUMMARY_MAX = 150


def build_skill_to_domain(categories_md: Path) -> dict[str, str]:
    """Parse CATEGORIES.md into {skill_name: domain}. First domain wins."""
    mapping: dict[str, str] = {}
    if not categories_md.exists():
        return mapping
    current = None
    for line in categories_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and line[3:].strip():
            current = line[3:].strip()
            continue
        if current and "`" in line:
            for name in SKILL_TOKEN.findall(line):
                mapping.setdefault(name, current)
    return mapping


def extract_detail_sections(lines: list[str], frontmatter_end: int) -> list[str]:
    """Return top-level `## ` header names from the body."""
    sections: list[str] = []
    for raw in lines[frontmatter_end:]:
        stripped = raw.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            name = stripped[3:].strip()
            if name and name not in sections:
                sections.append(name)
    return sections


def find_frontmatter_end(lines: list[str]) -> int:
    """Return the line index just after the closing `---` (0 if no frontmatter)."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def first_sentence(text: str, cap: int = SUMMARY_MAX) -> str:
    """Trim text to its first sentence, or truncate to `cap` chars."""
    text = text.strip()
    if not text:
        return ""
    parts = SENTENCE_END.split(text, maxsplit=1)
    candidate = parts[0].strip()
    if len(candidate) <= cap:
        return candidate
    # hard truncate on word boundary
    truncated = candidate[:cap].rsplit(" ", 1)[0]
    return truncated.rstrip(",;:") + "…"


def propose_summary(fm: dict, body_lines: list[str]) -> str:
    """Prefer the first sentence of `description`; fall back to the first
    non-empty paragraph after the first `# ` title."""
    desc = fm.get("description", "")
    if isinstance(desc, str) and desc.strip():
        return first_sentence(desc)
    for i, raw in enumerate(body_lines):
        if raw.strip() and not raw.startswith("#"):
            return first_sentence(raw.strip())
    return ""


_YAML_RESERVED = {"true", "false", "null", "yes", "no", "on", "off", "~"}
_DATE_LIKE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")
_NUMERIC_LIKE = re.compile(r"^-?\d+(\.\d+)?$")


def yaml_escape(value: str) -> str:
    """Wrap scalars that need quoting; leave simple kebab-case alone.
    Quotes date-like, numeric, and reserved-word scalars so strict YAML
    parsers don't coerce them to non-string types."""
    if not value:
        return '""'
    needs_quote = (
        any(c in value for c in ":#\"'\n[]{},&*?|>%@`")
        or value != value.strip()
        or _DATE_LIKE.match(value) is not None
        or _NUMERIC_LIKE.match(value) is not None
        or value.lower() in _YAML_RESERVED
    )
    if needs_quote:
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return value


def render_block(fm: dict, proposed: dict) -> str:
    """Render the full frontmatter block (existing keys + extension)."""
    merged = dict(fm)
    merged.update(proposed)

    lines = ["---"]
    for key, value in merged.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {yaml_escape(str(item))}")
        else:
            lines.append(f"{key}: {yaml_escape(str(value))}")
    lines.append("---")
    return "\n".join(lines)


def generate(skill_md: Path) -> tuple[str, dict]:
    """Return (rendered block, proposed fields)."""
    if not skill_md.exists():
        raise FileNotFoundError(skill_md)

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    total_lines = len(lines)

    fm, _ = parse_frontmatter(skill_md)
    fm_end = find_frontmatter_end(lines)
    body_lines = lines[fm_end:]

    skill_to_domain = build_skill_to_domain(CATEGORIES_MD)
    folder_name = skill_md.parent.name

    proposed = {
        "domain": skill_to_domain.get(folder_name, "uncategorised"),
        "size_class": size_class_for(total_lines),
        "summary": propose_summary(fm, body_lines),
        "detail_sections": extract_detail_sections(lines, fm_end),
    }

    return render_block(fm, proposed), proposed


def rewrite_in_place(skill_md: Path, new_block: str) -> None:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)
    fm_end = find_frontmatter_end(lines)
    if fm_end == 0:
        # no existing frontmatter — prepend
        body = text
        new_content = new_block + "\n\n" + body
    else:
        body = "\n".join(lines[fm_end:])
        new_content = new_block + "\n" + body
    if not new_content.endswith("\n"):
        new_content += "\n"
    skill_md.write_text(new_content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Propose extended frontmatter for a SKILL.md."
    )
    parser.add_argument("skill_md", help="Path to Teams/skills/<name>/SKILL.md")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Rewrite the SKILL.md in place with the proposed block.",
    )
    args = parser.parse_args()

    skill_md = Path(args.skill_md).resolve()
    try:
        block, proposed = generate(skill_md)
    except FileNotFoundError:
        print(f"error: file not found: {skill_md}", file=sys.stderr)
        return 1

    if args.write:
        rewrite_in_place(skill_md, block)
        print(f"wrote proposed frontmatter to {skill_md}")
        print(f"  domain:          {proposed['domain']}")
        print(f"  size_class:      {proposed['size_class']}")
        print(f"  summary:         {proposed['summary']}")
        print(f"  detail_sections: {len(proposed['detail_sections'])} section(s)")
        if proposed["domain"] == "uncategorised":
            print(
                "  warning: skill is not listed in CATEGORIES.md — domain set to "
                "'uncategorised'. Edit manually if this is wrong.",
                file=sys.stderr,
            )
        return 0

    print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
