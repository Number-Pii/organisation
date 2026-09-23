#!/usr/bin/env python3
"""PreToolUse hook (Claude Code): stop commits and pushes that land on main.

An optional convenience layer. The real guarantee is branch protection on the
hosting service, and the git-native `.githooks/pre-push` hook covers every
agent and person. This hook catches the mistake earlier, inside the session.

It inspects the repository each git command actually targets (`git -C <dir>`,
or a leading `cd <dir> &&`), so agents working in linked worktrees on their own
branches are not blocked by the branch of the session's starting folder.

Exit codes: 0 allows the tool call, 2 blocks it (stderr is shown to the agent).
"""

import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}
SEPARATORS = re.compile(r"&&|\|\||;|\||\n")


def branch_of(directory: str) -> str:
    try:
        result = subprocess.run(["git", "-C", directory, "branch", "--show-current"],
                                capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return ""


def git_calls(command: str):
    """Yield (directory, git_args) for each git invocation in a shell command."""
    directory = os.getcwd()
    for segment in SEPARATORS.split(command):
        try:
            words = shlex.split(segment)
        except ValueError:
            continue
        if not words:
            continue
        if words[0] == "cd" and len(words) > 1:
            directory = os.path.join(directory, os.path.expanduser(words[1]))
            continue
        if os.path.basename(words[0]) != "git":
            continue
        args, target, i = words[1:], directory, 0
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                target = os.path.join(target, os.path.expanduser(args[i + 1]))
                i += 2
            elif args[i] == "-c" and i + 1 < len(args):
                i += 2
            else:
                i += 1
        yield target, args[i:]


def pushes_to_protected(push_args) -> bool:
    for arg in push_args:
        if arg.startswith("-"):
            continue
        dest = arg.split(":", 1)[1] if ":" in arg else arg
        if dest.removeprefix("refs/heads/") in PROTECTED:
            return True
    return False


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

    for directory, args in git_calls(command):
        if not args:
            continue
        verb, rest = args[0], args[1:]
        if verb == "push":
            if pushes_to_protected(rest):
                block("Blocked: this push targets main. Push a feature/, fix/, chore/ "
                      "or hotfix/ branch and open a pull request.")
            if not [a for a in rest if not a.startswith("-")][1:] and branch_of(directory) in PROTECTED:
                block("Blocked: pushing from main. Create a branch (feature/, fix/, "
                      "chore/, hotfix/) and push that instead.")
        if verb == "commit" and branch_of(directory) in PROTECTED:
            block("Blocked: committing directly on main. Create a branch (feature/, "
                  "fix/, chore/, hotfix/) first; see doc/version_control.md.")
    sys.exit(0)


if __name__ == "__main__":
    main()
