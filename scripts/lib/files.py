"""File writing shared by the generators.

Generators must never touch a file whose content has not changed: a rewrite
with identical bytes is harmless to git, but it bumps mtimes, wakes file
watchers, and trains contributors to expect churn from routine runs.
"""

from pathlib import Path


def write_if_changed(path: Path, content: str) -> bool:
    """Write `content` to `path` only when it differs; return True if written."""
    try:
        if path.read_text(encoding="utf-8") == content:
            return False
    except (FileNotFoundError, UnicodeDecodeError):
        pass
    path.write_text(content, encoding="utf-8")
    return True
