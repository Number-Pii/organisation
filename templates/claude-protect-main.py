#!/usr/bin/env python3
"""PreToolUse hook: enforce the Version Control Discipline standard in code.

Blocks git commits and pushes that target a protected branch (main or master),
matching the rules in doc/version_control.md. Scaffolded by the Number Pii
toolkit; the prose contract still applies to assistants that ignore hooks.

Exit codes: 0 allows the tool call, 2 blocks it (stderr is shown to the agent).
"""

import json
import re
import subprocess
import sys

PROTECTED = ("main", "master")


def current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") != "Bash":
        sys.exit(0)
    command = (payload.get("tool_input") or {}).get("command") or ""

    protected_ref = re.compile(r"\b(main|master)\b")

    if re.search(r"\bgit\b[^|;&]*\bpush\b", command):
        if protected_ref.search(command.split("push", 1)[1]):
            block(
                "Blocked by the toolkit: this push targets a protected branch. "
                "doc/version_control.md requires a feature branch and a PR; "
                "no direct pushes to main, no exceptions."
            )
        if current_branch() in PROTECTED:
            block(
                "Blocked by the toolkit: pushing while checked out on a protected "
                "branch. Create a branch (feature/, fix/, chore/, hotfix/) first; "
                "see doc/version_control.md."
            )

    if re.search(r"\bgit\b[^|;&]*\bcommit\b", command) and current_branch() in PROTECTED:
        block(
            "Blocked by the toolkit: committing directly on a protected branch. "
            "Create a branch (feature/, fix/, chore/, hotfix/) first; "
            "see doc/version_control.md."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
