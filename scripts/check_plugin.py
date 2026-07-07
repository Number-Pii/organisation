#!/usr/bin/env python3
"""
check_plugin.py: Number Pii Plugin Packaging Validator

Checks the Claude Code plugin packaging that no other CI step executes:
  - .claude-plugin/plugin.json parses and carries non-empty name and version
  - hooks/hooks.json parses and every ${CLAUDE_PLUGIN_ROOT} script it
    references resolves to a file in this repo
  - commands/init.md exists and is non-empty
  - agents/ contains at least one generated np-*.md subagent
  - hooks/protect_main.py and templates/claude-protect-main.py are
    byte-identical (the plugin copy and the scaffold copy ship separately
    on purpose, but they must not drift apart)

Exit code 0 = packaging valid, 1 = at least one check failed.

Usage:
    python3 scripts/check_plugin.py
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)")


def iter_strings(node):
    """Yield every string value nested anywhere in parsed JSON."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from iter_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_strings(item)


def check_manifest():
    """Validate .claude-plugin/plugin.json parses and has name and version."""
    errors = []
    path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    if not path.exists():
        return [f"  missing manifest: {path.relative_to(REPO_ROOT)}"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"  .claude-plugin/plugin.json is not valid JSON: {exc}"]
    for key in ("name", "version"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"  .claude-plugin/plugin.json needs a non-empty '{key}' field"
            )
    return errors


def check_hooks():
    """Validate hooks/hooks.json parses and its referenced scripts exist."""
    errors = []
    path = REPO_ROOT / "hooks" / "hooks.json"
    if not path.exists():
        return [f"  missing hook config: {path.relative_to(REPO_ROOT)}"]
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"  hooks/hooks.json is not valid JSON: {exc}"]
    refs = [
        ref
        for value in iter_strings(config)
        for ref in PLUGIN_ROOT_REF.findall(value)
    ]
    if not refs:
        errors.append(
            "  hooks/hooks.json references no ${CLAUDE_PLUGIN_ROOT} scripts;"
            " expected at least the main-branch protection hook"
        )
    for ref in refs:
        target = REPO_ROOT / ref
        if not target.is_file():
            errors.append(
                f"  hooks/hooks.json references {ref}, which does not exist"
            )
    return errors


def check_command():
    """Validate the /init command file exists and is non-empty."""
    path = REPO_ROOT / "commands" / "init.md"
    if not path.exists():
        return [f"  missing command file: {path.relative_to(REPO_ROOT)}"]
    if not path.read_text(encoding="utf-8").strip():
        return ["  commands/init.md is empty"]
    return []


def check_agents():
    """Validate at least one generated np-*.md subagent is present."""
    agents_dir = REPO_ROOT / "agents"
    if not agents_dir.is_dir():
        return ["  missing agents/ directory"]
    if not sorted(agents_dir.glob("np-*.md")):
        return ["  agents/ has no np-*.md files; run scripts/build_agents.py"]
    return []


def check_protect_main_copies():
    """Validate the plugin and scaffold copies of protect_main are identical.

    hooks/protect_main.py runs inside the installed plugin;
    templates/claude-protect-main.py is scaffolded into consuming projects by
    init_project.py. Both must carry the same logic. Treat the hooks/ copy as
    the source: edit it first, then copy it over the templates/ file.
    """
    plugin_copy = REPO_ROOT / "hooks" / "protect_main.py"
    scaffold_copy = REPO_ROOT / "templates" / "claude-protect-main.py"
    missing = [
        f"  missing file: {p.relative_to(REPO_ROOT)}"
        for p in (plugin_copy, scaffold_copy)
        if not p.exists()
    ]
    if missing:
        return missing
    if plugin_copy.read_bytes() != scaffold_copy.read_bytes():
        return [
            "  hooks/protect_main.py and templates/claude-protect-main.py"
            " have drifted apart; edit hooks/protect_main.py, then copy it"
            " over templates/claude-protect-main.py"
        ]
    return []


def main():
    errors = (
        check_manifest()
        + check_hooks()
        + check_command()
        + check_agents()
        + check_protect_main_copies()
    )

    if errors:
        print("PLUGIN PACKAGING CHECK FAILED:")
        for e in errors:
            print(e)
        sys.exit(1)
    print("Plugin packaging valid: manifest, hooks, command, agents,"
          " protect-main copies in sync.")
    sys.exit(0)


if __name__ == "__main__":
    main()
