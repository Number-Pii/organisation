# Skills

Skills are instruction sets, sometimes with bundled scripts, that an agent loads
when a task calls for them. Each lives in its own folder with a `SKILL.md`.

This library is small on purpose. A skill is kept only when it gives a current
frontier model something it lacks: working scripts or assets, tool-specific
knowledge that changes quickly, a Number Pii process, or the canonical approach
to a topic where consistency matters. [CATEGORIES.md](CATEGORIES.md) lists them
by domain; `skills-index.json` is the machine-readable form. Both are generated.

## Finding and using a skill

```bash
python3 scripts/find_skill.py <keyword>            # search names and summaries
python3 scripts/find_skill.py --domain "Testing & QA" <keyword>
```

Then read that skill's `SKILL.md` and follow it. Role files under `Teams/` link
the skills relevant to each role as `@skill-name`. The frontmatter follows the
open Agent Skills convention, so Claude Code and Codex can also load these
folders through their own skill mechanisms.

## Adding, reviewing, and removing

See [CONTRIBUTING.md](../../CONTRIBUTING.md#adding-a-new-skill). Every skill
carries a reviewed `risk` and a `last_reviewed` date, and is re-read in the
quarterly review. Skills removed in the 4.x prune remain recoverable from the
`v3-skills-full` tag.
