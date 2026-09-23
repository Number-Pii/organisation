"""Runner adapters for headless coding agents (Claude Code, OpenAI Codex).

One interface for every runner: `run()` executes a prompt in a working
directory and returns a RunResult with a normalised event list (reads, edits,
shell commands, searches), the final reply, and usage. Scenario evals and skill
evals both go through here, so no script hard-codes one vendor's CLI.

Safety: runs are meant for throwaway scratch directories. Claude gets
`acceptEdits` plus a scoped Bash allowlist (never --dangerously-skip-permissions);
Codex keeps its workspace-write sandbox, with only the scratch repo's `.git`
and any listed directories added as writable.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

RUNNERS = ("claude", "codex")

# Commands a scenario agent may run under Claude. Anything else is denied in
# headless mode, which is itself an observable signal in the transcript.
CLAUDE_ALLOWED_TOOLS = [
    "Read", "Edit", "Write", "MultiEdit", "Glob", "Grep", "TodoWrite", "NotebookEdit",
    "Bash(git *)", "Bash(python3 *)", "Bash(python *)", "Bash(ls *)", "Bash(cat *)",
    "Bash(head *)", "Bash(tail *)", "Bash(wc *)", "Bash(find *)", "Bash(grep *)",
    "Bash(rg *)", "Bash(sed *)", "Bash(mkdir *)", "Bash(mv *)", "Bash(cp *)",
    "Bash(echo *)", "Bash(diff *)", "Bash(pwd)", "Bash(tree *)",
]

READ_TOOLS = {"Read", "NotebookRead"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SEARCH_TOOLS = {"Grep", "Glob", "LS"}
READER_COMMANDS = {"cat", "sed", "head", "tail", "nl", "less", "more", "bat", "awk",
                   "rg", "grep", "wc", "diff", "view"}


@dataclass
class Event:
    kind: str                      # read | edit | shell | search
    path: str | None = None        # workspace-relative where known
    cmd: str | None = None


@dataclass
class RunResult:
    runner: str
    exit_code: int
    events: list[Event] = field(default_factory=list)
    final_text: str = ""
    usage: dict = field(default_factory=dict)
    turns: int | None = None
    cost_usd: float | None = None
    seconds: float = 0.0
    timed_out: bool = False
    model: str | None = None


def available(runner: str) -> bool:
    return shutil.which(runner) is not None


def command(runner: str, workdir: Path, prompt: str, model: str | None = None,
            writable: tuple[Path, ...] = ()) -> list[str]:
    if runner == "claude":
        cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--permission-mode", "acceptEdits", "--setting-sources", "project",
               "--no-session-persistence"]
        # `writable` is the scratch run dir: the repo, its bare origin, and any
        # sibling worktrees an agent creates for parallel work. Nothing beyond.
        for extra in writable:
            cmd += ["--add-dir", str(extra)]
        cmd += ["--allowedTools", *CLAUDE_ALLOWED_TOOLS]
        return cmd + (["--model", model] if model else [])
    if runner == "codex":
        cmd = ["codex", "exec", "--json", "--ephemeral", "-s", "workspace-write",
               "-C", str(workdir), "--add-dir", str(workdir / ".git")]
        for extra in writable:
            cmd += ["--add-dir", str(extra)]
        return cmd + (["-m", model] if model else []) + [prompt]
    raise ValueError(f"unknown runner {runner!r}; expected one of {RUNNERS}")


def run(runner: str, workdir: Path, prompt: str, *, transcript: Path,
        timeout: int = 1800, model: str | None = None,
        writable: tuple[Path, ...] = ()) -> RunResult:
    """Run one prompt headlessly in `workdir`; raw JSONL goes to `transcript`."""
    workdir = Path(workdir)
    transcript.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timed_out = False
    with transcript.open("w", encoding="utf-8") as out:
        proc = subprocess.Popen(
            command(runner, workdir, prompt, model, writable), cwd=workdir,
            stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, text=True,
        )
        try:
            exit_code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            exit_code = proc.wait()
            timed_out = True
    result = parse(runner, transcript.read_text(encoding="utf-8", errors="replace"), workdir)
    result.exit_code = exit_code
    result.seconds = round(time.monotonic() - started, 1)
    result.timed_out = timed_out
    return result


def ask(runner: str, prompt: str, *, transcript: Path, timeout: int = 900,
        model: str | None = None) -> str:
    """Plain question and answer in an empty scratch dir (skill A/B evals)."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        result = run(runner, Path(tmp), prompt, transcript=transcript,
                     timeout=timeout, model=model)
    if result.exit_code != 0 and not result.final_text:
        return f"[run failed, exit {result.exit_code}; see {transcript}]"
    return result.final_text


# ── transcript parsing ───────────────────────────────────────────────────────

def parse(runner: str, raw: str, workdir: Path) -> RunResult:
    lines = [json.loads(l) for l in raw.splitlines() if l.strip().startswith("{") and _json_ok(l)]
    if runner == "claude":
        return _parse_claude(lines, workdir)
    return _parse_codex(lines, workdir)


def _json_ok(line: str) -> bool:
    try:
        json.loads(line)
        return True
    except ValueError:
        return False


def _parse_claude(lines: list[dict], workdir: Path) -> RunResult:
    result = RunResult("claude", 0)
    for e in lines:
        kind = e.get("type")
        if kind == "system" and e.get("subtype") == "init":
            result.model = e.get("model")
        elif kind == "assistant":
            for block in e.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name, args = block.get("name", ""), block.get("input", {}) or {}
                path = args.get("file_path") or args.get("notebook_path")
                if name in READ_TOOLS:
                    result.events.append(Event("read", rel(path, workdir)))
                elif name in EDIT_TOOLS:
                    result.events.append(Event("edit", rel(path, workdir)))
                elif name in SEARCH_TOOLS:
                    result.events.append(Event("search", rel(args.get("path"), workdir),
                                               args.get("pattern")))
                elif name == "Bash":
                    result.events.extend(shell_events(args.get("command", ""), workdir))
        elif kind == "result":
            result.final_text = str(e.get("result") or "")
            result.usage = e.get("usage") or {}
            result.turns = e.get("num_turns")
            result.cost_usd = e.get("total_cost_usd")
    return result


def _parse_codex(lines: list[dict], workdir: Path) -> RunResult:
    result = RunResult("codex", 0)
    usage: dict = {}
    turns = 0
    messages: list[str] = []
    for e in lines:
        kind = e.get("type")
        item = e.get("item") or {}
        if kind == "turn.completed":
            turns += 1
            for key, value in (e.get("usage") or {}).items():
                if isinstance(value, (int, float)):
                    usage[key] = usage.get(key, 0) + value
        if kind != "item.completed":
            continue
        itype = item.get("type")
        if itype == "command_execution":
            result.events.extend(shell_events(unwrap_shell(item.get("command", "")), workdir))
        elif itype == "file_change":
            for change in item.get("changes", []):
                result.events.append(Event("edit", rel(change.get("path"), workdir)))
        elif itype == "agent_message":
            messages.append(item.get("text", ""))
    result.final_text = messages[-1] if messages else ""
    result.usage = usage
    result.turns = turns or None
    return result


def unwrap_shell(command_line: str) -> str:
    """Codex wraps commands as `/bin/zsh -lc "..."`; return the inner script."""
    try:
        parts = shlex.split(command_line)
    except ValueError:
        return command_line
    if len(parts) >= 3 and parts[0].endswith(("sh", "bash", "zsh")) and parts[1] in ("-lc", "-c"):
        return parts[2]
    return command_line


def shell_events(script: str, workdir: Path) -> list[Event]:
    """One shell event, plus a read event per existing file a reader command names."""
    events = [Event("shell", cmd=script)]
    for segment in _segments(script):
        try:
            words = shlex.split(segment)
        except ValueError:
            continue
        if not words or os.path.basename(words[0]) not in READER_COMMANDS:
            continue
        for word in words[1:]:
            if word.startswith("-"):
                continue
            candidate = (workdir / word) if not os.path.isabs(word) else Path(word)
            if candidate.is_file():
                events.append(Event("read", rel(str(candidate), workdir)))
    return events


def _segments(script: str) -> list[str]:
    for sep in ("&&", "||", ";", "|", "\n"):
        script = script.replace(sep, "\x00")
    return [s.strip() for s in script.split("\x00") if s.strip()]


def rel(path: str | None, workdir: Path) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        return p.as_posix()
    for root in {workdir, workdir.resolve()}:
        try:
            return p.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            try:
                return p.relative_to(root).as_posix()
            except ValueError:
                continue
    return p.as_posix()
