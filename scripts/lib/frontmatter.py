"""Zero-dependency frontmatter parsing shared by the skill tooling.

Handles the subset of YAML used in SKILL.md files: flat scalar keys,
flow sequences (`[a, b]`), and one-level block lists (`- item`).
"""

from pathlib import Path

VALID_SIZE_CLASSES = {"xs", "s", "m", "l", "xl"}


def size_class_for(line_count: int) -> str:
    """Band line counts: <50 xs, 50-199 s, 200-499 m, 500-999 l, 1000+ xl."""
    if line_count < 50:   return "xs"
    if line_count < 200:  return "s"
    if line_count < 500:  return "m"
    if line_count < 1000: return "l"
    return "xl"


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _parse_scalar(value: str):
    # Flow sequence: [a, b, c]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [_unquote(item.strip()) for item in inner.split(",") if item.strip()]
    return _unquote(value)


def parse_frontmatter(path: Path):
    """
    Return (frontmatter_dict, total_line_count).
    Handles the subset of YAML used in SKILL.md files: flat scalar keys and
    one-level block lists (`- item`). Returns ({}, total) if no frontmatter.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}, 0

    lines = text.splitlines()
    total = len(lines)

    if not lines or lines[0].strip() != "---":
        return {}, total

    end = None
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, total

    fm: dict = {}
    current_list_key = None
    for raw in lines[1:end]:
        stripped = raw.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            continue

        # list item under the most recent empty-value key
        lstripped = stripped.lstrip()
        if current_list_key and lstripped.startswith("- "):
            fm[current_list_key].append(_unquote(lstripped[2:].strip()))
            continue

        # top-level key: value
        if ":" in stripped and not stripped.startswith((" ", "\t")):
            key, _, rest = stripped.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest == "":
                fm[key] = []
                current_list_key = key
            else:
                fm[key] = _parse_scalar(rest)
                current_list_key = None

    return fm, total
