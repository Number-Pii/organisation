---
description: Run the Number Pii Initialize Protocol (INITIALIZE.md) step by step
---

Run the Number Pii Initialize Protocol.

1. Read `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md` in full and acknowledge it as the protocol requires.
2. Read `${CLAUDE_PLUGIN_ROOT}/INITIALIZE.md` in full. Do not run the protocol from memory; if the file is missing, stop and escalate.
3. Execute its steps exactly, in order: welcome, project brief, brownfield intake when applicable, project classification (Levels 1 to 4), team assignment, scaffolding via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py` (always pass `--output-dir` pointing at the consuming project, never the toolkit), doc population, and the execution board step.
4. Apply the user's arguments to the protocol: $ARGUMENTS
