#!/usr/bin/env python3
"""
check_writing.py: Number Pii Writing Standard Validator

Checks prose deliverables (markdown or plain text) against WRITING.md:
  FAIL  em dashes, en dashes, banned phrases, 3+ consecutive identical sentence openers
  WARN  Flesch Reading Ease outside the target band, low sentence-length variety,
        dominant sentence opener, high passive-voice ratio (approximate)

The banned-phrases list is read live from WRITING.md (between the
BANNED-PHRASES:START/END markers), so the standard has a single source of truth.

Scope (WRITING.md, "Scope"): only text you author is checked. Blocks managed
by other tools (<!-- BEGIN:name --> ... <!-- END:name -->) and the toolkit's own
managed block (<!-- np:begin --> ... <!-- np:end -->) are skipped, and files in
generated, vendored, or dependency paths are skipped unless --no-default-excludes
is given. CI, the pre-commit hook, and consumer projects all get the same scope
because it lives here.

Usage:
    python3 scripts/check_writing.py FILE [FILE ...]
    python3 scripts/check_writing.py FILE --profile marketing   # Flesch 50-65
    python3 scripts/check_writing.py FILE --strict              # WARN also fails

Exit codes:
    0: all files pass
    1: at least one FAIL (or WARN with --strict), or input error
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WRITING_MD = REPO_ROOT / "WRITING.md"

EM_DASH = "—"
EN_DASH = "–"

VOWELS = "aeiouy"

PASSIVE_RE = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\s+(\w+ed|\w+en)\b", re.IGNORECASE
)

# Rule statements that name the dash characters, e.g. "no em dashes (—)", are
# mentions rather than uses; strip them before scanning so the standard's own
# text (WRITING.md, CLAUDE.md, scripts/README.md) does not flag itself.
DASH_MENTION_RE = re.compile(r"[Ee][mn] dash(es)?\s*\((?:—|–)\)")

# Text owned by another tool or by the toolkit's sync step, not by the author.
MANAGED_BEGIN_RE = re.compile(r"<!--\s*(?:BEGIN:(\S+)|np:begin)\s*-->")

# Paths that hold generated, vendored, or dependency content.
DEFAULT_EXCLUDES = [
    "*/node_modules/*", "node_modules/*", "*/vendor/*", "vendor/*",
    "*/dist/*", "dist/*", "*/build/*", "build/*", "*/.next/*", ".next/*",
    "*.lock", "*package-lock.json", "*pnpm-lock.yaml", "*/.venv/*", ".venv/*",
]

PROFILES = {"technical": (30.0, 40.0), "marketing": (50.0, 65.0), "internal": (35.0, 55.0)}


def excluded(path: Path) -> bool:
    posix = path.as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in DEFAULT_EXCLUDES)


def strip_managed_blocks(raw: str) -> str:
    """Blank out managed regions, keeping line numbers stable for reporting."""
    lines = raw.splitlines()
    out = []
    end_marker = None
    for line in lines:
        # Markers quoted in inline code are mentions, not real block boundaries.
        live = re.sub(r"`[^`]*`", "", line)
        if end_marker is None:
            m = MANAGED_BEGIN_RE.search(live)
            if m:
                name = m.group(1)
                end_marker = (re.compile(rf"<!--\s*END:{re.escape(name)}\s*-->") if name
                              else re.compile(r"<!--\s*np:end\s*-->"))
                out.append("")
                if end_marker.search(live[m.end():]):
                    end_marker = None
                continue
            out.append(line)
        else:
            out.append("")
            if end_marker.search(live):
                end_marker = None
    return "\n".join(out)


def load_banned_phrases() -> list[str]:
    if not WRITING_MD.exists():
        sys.exit(f"ERROR: {WRITING_MD} not found; the validator needs the standard file.")
    text = WRITING_MD.read_text(encoding="utf-8")
    m = re.search(
        r"<!-- BANNED-PHRASES:START -->(.*?)<!-- BANNED-PHRASES:END -->",
        text,
        re.DOTALL,
    )
    if not m:
        sys.exit("ERROR: BANNED-PHRASES markers not found in WRITING.md.")
    phrases = re.findall(r"^- `([^`]+)`", m.group(1), re.MULTILINE)
    if not phrases:
        sys.exit("ERROR: banned-phrases block in WRITING.md is empty or malformed.")
    return phrases


def phrase_pattern(phrase: str) -> re.Pattern:
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def scannable_lines(raw: str) -> list[tuple[int, str]]:
    """Original lines minus fenced code blocks, inline code, and HTML comments,
    keeping 1-based line numbers for reporting."""
    out = []
    in_fence = False
    in_comment = False
    for i, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Track multi-line HTML comments (used for template guidance and markers).
        if in_comment:
            if "-->" in line:
                line = line.split("-->", 1)[1]
                in_comment = False
            else:
                continue
        line = re.sub(r"<!--.*?-->", "", line)
        if "<!--" in line:
            line = line.split("<!--", 1)[0]
            in_comment = True
        line = re.sub(r"`[^`]*`", "", line)        # inline code
        line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)  # images
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)  # links: keep text
        out.append((i, line))
    return out


def prose_sentences(lines: list[tuple[int, str]]) -> list[str]:
    """Sentences from prose content: headings, table rows, and blank lines excluded;
    list items count as sentences."""
    chunks = []
    for _, line in lines:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or set(s) <= {"-", "=", "*", "_", " "}:
            continue
        s = re.sub(r"^(?:[-*+]|\d+\.)\s+", "", s)  # list markers
        s = re.sub(r"^>\s*", "", s)                # blockquote markers
        if s:
            chunks.append(s)
    text = " ".join(chunks)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(p.split()) >= 2]


def count_syllables(word: str) -> int:
    w = word.lower().strip("'")
    if not w:
        return 0
    groups = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and groups > 1:
        groups -= 1
    return max(1, groups)


def flesch_reading_ease(sentences: list[str]) -> float | None:
    words = []
    for s in sentences:
        words.extend(re.findall(r"[A-Za-z']+", s))
    if not sentences or len(words) < 30:
        return None
    syllables = sum(count_syllables(w) for w in words)
    return 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))


def check_file(path: Path, banned: list[str], target: tuple[float, float]) -> tuple[list[str], list[str], list[str]]:
    """Returns (fails, warns, infos) finding lists for one file."""
    raw = strip_managed_blocks(path.read_text(encoding="utf-8"))
    lines = scannable_lines(raw)
    fails: list[str] = []
    warns: list[str] = []
    infos: list[str] = []

    # Dashes (hard rule from the Writing Style standard).
    for lineno, line in lines:
        clean = DASH_MENTION_RE.sub("dash", line)
        if EM_DASH in clean:
            fails.append(f"Em dash (—) at line {lineno}")
        if EN_DASH in clean:
            fails.append(f"En dash (–) at line {lineno}")

    # Banned phrases.
    patterns = [(p, phrase_pattern(p)) for p in banned]
    for lineno, line in lines:
        for phrase, pat in patterns:
            if pat.search(line):
                fails.append(f'Banned phrase "{phrase}" at line {lineno}')

    sentences = prose_sentences(lines)
    if len(sentences) >= 3:
        openers = [re.sub(r"^\W+", "", s).split()[0].lower() if s.split() else "" for s in sentences]

        run_word, run_len = None, 0
        for w in openers:
            if w and w == run_word:
                run_len += 1
                if run_len == 3:
                    fails.append(f'Three consecutive sentences open with "{run_word}"')
            else:
                run_word, run_len = w, 1

        if len(sentences) >= 10:
            top = max(set(openers), key=openers.count)
            share = openers.count(top) / len(openers)
            if share > 0.3:
                warns.append(f'Opener "{top}" starts {share:.0%} of sentences (keep any opener under 30%)')

        lengths = [len(s.split()) for s in sentences]
        if len(lengths) >= 8:
            stdev = statistics.pstdev(lengths)
            mean = statistics.mean(lengths)
            if stdev < 4 and mean > 12:
                warns.append(
                    f"Low sentence-length variety (mean {mean:.0f} words, spread {stdev:.1f}); vary deliberately"
                )

        passive = sum(1 for s in sentences if PASSIVE_RE.search(s))
        ratio = passive / len(sentences)
        if ratio > 0.3:
            warns.append(f"Passive voice in ~{ratio:.0%} of sentences (approximate); favour active voice")
        else:
            infos.append(f"Passive voice (approximate): {ratio:.0%} of sentences")

    score = flesch_reading_ease(sentences)
    lo, hi = target
    if score is None:
        infos.append("Flesch Reading Ease: not enough prose to score (needs ~30+ words)")
    elif lo <= score <= hi:
        infos.append(f"Flesch Reading Ease: {score:.1f} (target {lo:.0f}-{hi:.0f})")
    else:
        warns.append(f"Flesch Reading Ease {score:.1f} outside target {lo:.0f}-{hi:.0f}")

    return fails, warns, infos


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate prose against the Number Pii Writing Standard")
    parser.add_argument("files", nargs="+", help="Markdown or plain-text files to check")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="technical",
                        help="Readability target by document type (WRITING.md calibration table)")
    parser.add_argument("--target-min", type=float, help="Override the profile's Flesch lower bound")
    parser.add_argument("--target-max", type=float, help="Override the profile's Flesch upper bound")
    parser.add_argument("--no-default-excludes", action="store_true",
                        help="Also check files in generated, vendored, and dependency paths")
    parser.add_argument("--strict", action="store_true", help="Treat WARN findings as failures")
    args = parser.parse_args()

    banned = load_banned_phrases()
    lo, hi = PROFILES[args.profile]
    target = (args.target_min if args.target_min is not None else lo,
              args.target_max if args.target_max is not None else hi)
    exit_code = 0

    for name in args.files:
        path = Path(name)
        if not path.exists():
            print(f"ERROR: {path} not found")
            exit_code = 1
            continue
        if not args.no_default_excludes and excluded(path):
            print(f"\n── check_writing: {path} ── skipped (generated, vendored, or dependency path)")
            continue

        fails, warns, infos = check_file(path, banned, target)

        print(f"\n── check_writing: {path} ──")
        for f in fails:
            print(f"  FAIL  {f}")
        for w in warns:
            print(f"  WARN  {w}")
        for i in infos:
            print(f"  info  {i}")

        failed = bool(fails) or (args.strict and bool(warns))
        verdict = "FAIL" if failed else "PASS"
        print(f"  Summary: {len(fails)} FAIL, {len(warns)} WARN → {verdict}")
        if failed:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
