#!/usr/bin/env python3
"""
docs.py: Number Pii Documentation Map and Check

Keeps a project's documentation connected. The graph is:

    AGENTS.md -> doc/README.md -> known folders (decisions/, specs/, ...) -> documents

A file inside a folder that doc/README.md lists is found by listing that
folder, so adding one needs no index edit and parallel PRs never collide on a
shared table. Only a new top-level doc/ file, or a new folder, needs a row in
doc/README.md.

Subcommands:
    map     Print every document with a one-line summary (never committed)
    check   Fail on orphaned documents and broken relative links

In a repository without doc/README.md (the toolkit itself), `check` instead
requires every top-level markdown file to be referenced from AGENTS.md or
README.md, and checks links in all maintained markdown.

Usage:
    python3 organisation/scripts/docs.py map
    python3 organisation/scripts/docs.py check
    python3 scripts/docs.py check --root .     # the toolkit's own tree
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.frontmatter import parse_frontmatter  # noqa: E402

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", ".next", "__pycache__",
             "organisation"}
# Vendored or fixture content, and templates whose links are written relative to
# a consuming project's layout: never checked for links.
EXCLUDED_PREFIXES = ("Teams/skills/", "evals/scenarios/fixture/", "tests/golden/", "tests/fixtures/",
                     "templates/")


def summary(path: Path) -> str:
    """Front matter `summary:`, else the first prose paragraph after the title."""
    fm, _ = parse_frontmatter(path)
    if fm.get("summary"):
        return str(fm["summary"])
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith(("#", "<!--", "|", ">", "```", "---")):
            continue
        line = " ".join(block.split())
        return line[:117] + "..." if len(line) > 120 else line
    return ""


def markdown_files(root: Path) -> list[Path]:
    tracked = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others",
                              "--exclude-standard", "*.md"], capture_output=True, text=True)
    if tracked.returncode == 0:
        names = [n for n in tracked.stdout.split("\0") if n]
        return [root / n for n in names if (root / n).is_file()]
    return [p for p in root.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(root).parts)]


def broken_links(root: Path, files: list[Path]) -> list[str]:
    problems = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if rel.startswith(EXCLUDED_PREFIXES):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in LINK_RE.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith(("#", "<")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            if not (path.parent / target_path).exists():
                problems.append(f"{rel}: broken link to {target}")
    return problems


def mentioned(name: str, text: str) -> bool:
    return re.search(rf"(?<![\w/.-]){re.escape(name)}", text) is not None


def doc_orphans(root: Path) -> list[str]:
    doc = root / "doc"
    readme = doc / "README.md"
    index = readme.read_text(encoding="utf-8")
    problems = []
    for child in sorted(doc.iterdir()):
        if child.name.startswith(".") or child == readme:
            continue
        name = child.name + ("/" if child.is_dir() else "")
        if child.is_dir():
            if not mentioned(child.name + "/", index) and not mentioned(child.name, index):
                problems.append(f"doc/{name} is not in doc/README.md; add a row for the folder")
        elif child.suffix == ".md" and not mentioned(child.name, index):
            problems.append(f"doc/{name} is not linked from doc/README.md; add a row or "
                            "move it into a folder the map lists")
    return problems


def missing_hub_mentions(root: Path) -> list[str]:
    """Bare `NAME.md` names quoted in AGENTS.md or README.md that match no file.

    Links are checked elsewhere; this catches references written as code, which
    is how agent instructions usually name files."""
    problems = []
    known = {p.name for p in markdown_files(root)}
    for hub in ("AGENTS.md", "README.md"):
        path = root / hub
        if not path.exists():
            continue
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
        for name in sorted(set(re.findall(r"`([A-Za-z0-9_-]+\.md)`", text))):
            if name not in known:
                problems.append(f"{hub} names `{name}`, which does not exist")
    return problems


def root_orphans(root: Path) -> list[str]:
    hubs = " ".join((root / n).read_text(encoding="utf-8") for n in ("AGENTS.md", "README.md")
                    if (root / n).exists())
    problems = []
    for path in sorted(root.glob("*.md")):
        if path.name in ("AGENTS.md", "README.md", "CLAUDE.md", "GEMINI.md"):
            continue
        if not mentioned(path.name, hubs):
            problems.append(f"{path.name} is not referenced from AGENTS.md or README.md")
    return problems


def cmd_map(args) -> int:
    root = Path(args.root).resolve()
    doc = root / "doc"
    if not doc.is_dir():
        print("No doc/ folder here.")
        return 1
    for path in sorted(doc.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        print(f"{rel}\n    {summary(path) or '(no summary)'}")
    return 0


def cmd_check(args) -> int:
    root = Path(args.root).resolve()
    files = markdown_files(root)
    problems = broken_links(root, files)
    if (root / "doc" / "README.md").exists():
        problems += doc_orphans(root)
    elif not (root / "doc").exists():
        problems += root_orphans(root) + missing_hub_mentions(root)
    else:
        problems.append("doc/ has no README.md map; scaffold one with init_project.py")
    for p in problems:
        print(f"FAIL  {p}")
    if not problems:
        print(f"OK: {len(files)} markdown files, no orphans, no broken links.")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Map and check project documentation")
    parser.add_argument("--root", default=".", help="Project root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("map", help="Print every doc with its summary").set_defaults(func=cmd_map)
    sub.add_parser("check", help="Fail on orphans and broken links").set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
