#!/usr/bin/env python3
"""
run_evals.py: Number Pii Skill Eval Runner

Runs the golden tasks in evals/tasks/ twice each: bare, and with the skill
under test loaded into the prompt. Results land in evals/results/<timestamp>/
as one markdown file per task, holding both outputs and the task's rubric for
judging. See evals/README.md for the method.

Runs through the shared runner adapters in scripts/lib/agents.py, so any
supported agent CLI works (`--runner claude` or `--runner codex`); --list
works without either.

Usage:
    python3 scripts/run_evals.py --list
    python3 scripts/run_evals.py --domain backend --runner codex
    python3 scripts/run_evals.py
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import agents  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
TASKS_DIR = REPO_ROOT / "evals" / "tasks"
RESULTS_DIR = REPO_ROOT / "evals" / "results"
SKILLS_DIR = REPO_ROOT / "Teams" / "skills"

TASK_RE = re.compile(r"^## Task:\s*(.+)$")
FIELD_RE = re.compile(r"^-\s+\*\*(Skill|Prompt|Rubric):\*\*\s*(.*)$")


def parse_tasks(path: Path) -> list[dict]:
    """Parse one evals/tasks/<domain>.md into task dicts:
    {slug, skill, prompt, rubric: [criteria]}."""
    tasks: list[dict] = []
    current: dict | None = None
    in_rubric = False
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TASK_RE.match(line.strip())
        if m:
            current = {"slug": m.group(1).strip(), "skill": "", "prompt": "", "rubric": []}
            tasks.append(current)
            in_rubric = False
            continue
        if current is None:
            continue
        f = FIELD_RE.match(line.strip())
        if f:
            field = f.group(1).lower()
            in_rubric = field == "rubric"
            if field == "skill":
                current["skill"] = f.group(2).strip().lstrip("@")
            elif field == "prompt":
                current["prompt"] = f.group(2).strip()
            continue
        if in_rubric and line.strip().startswith("- "):
            current["rubric"].append(line.strip()[2:].strip())
    return [t for t in tasks if t["prompt"] and t["rubric"]]


def skill_preamble(skill: str) -> str:
    skill_md = SKILLS_DIR / skill / "SKILL.md"
    if not skill_md.exists():
        return ""
    return (
        f"Apply the following skill while answering.\n\n"
        f"<skill name=\"{skill}\">\n{skill_md.read_text(encoding='utf-8')}\n</skill>\n\n"
    )


def result_doc(task: dict, bare: str, skilled: str) -> str:
    rubric = "\n".join(f"- [ ] {c}" for c in task["rubric"])
    return (
        f"# Eval: {task['slug']}\n\n"
        f"Skill under test: `@{task['skill']}`\n\n"
        f"## Prompt\n{task['prompt']}\n\n"
        f"## Rubric (score each output per criterion)\n{rubric}\n\n"
        f"## Output A: bare\n\n{bare}\n\n"
        f"## Output B: with skill\n\n{skilled}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the toolkit skill evals")
    parser.add_argument("--domain", help="Run one domain (a file under evals/tasks/)")
    parser.add_argument("--list", action="store_true", help="List tasks and exit")
    parser.add_argument("--runner", default="claude", choices=agents.RUNNERS,
                        help="Agent CLI to run the tasks with (default: claude)")
    args = parser.parse_args()

    task_files = sorted(TASKS_DIR.glob("*.md"))
    if args.domain:
        task_files = [f for f in task_files if f.stem == args.domain]
        if not task_files:
            sys.exit(f"ERROR: no evals/tasks/{args.domain}.md; "
                     f"domains: {', '.join(f.stem for f in sorted(TASKS_DIR.glob('*.md')))}")

    all_tasks = [(f.stem, t) for f in task_files for t in parse_tasks(f)]
    if args.list:
        for domain, task in all_tasks:
            print(f"{domain}/{task['slug']}  (@{task['skill']}, {len(task['rubric'])} criteria)")
        return 0

    if not agents.available(args.runner):
        sys.exit(f"ERROR: the `{args.runner}` CLI is not on PATH; live runs need it. "
                 "Use --list to inspect tasks.")

    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out_dir = RESULTS_DIR / f"{stamp}-skills-{args.runner}"
    out_dir.mkdir(parents=True)

    for domain, task in all_tasks:
        print(f"[{domain}/{task['slug']}] bare run...", flush=True)
        stem = out_dir / "transcripts" / f"{domain}--{task['slug']}"
        bare = agents.ask(args.runner, task["prompt"], transcript=stem.with_suffix(".bare.jsonl"))
        print(f"[{domain}/{task['slug']}] skill run...", flush=True)
        skilled = agents.ask(args.runner, skill_preamble(task["skill"]) + task["prompt"],
                             transcript=stem.with_suffix(".skill.jsonl"))
        (out_dir / f"{domain}--{task['slug']}.md").write_text(
            result_doc(task, bare, skilled), encoding="utf-8")

    print(f"\nWrote {len(all_tasks)} result file(s) to {out_dir}")
    print("Judge each file against its rubric; record verdicts before changing any tier.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
