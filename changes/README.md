# Changelog fragments

Every PR adds one file here instead of editing `CHANGELOG.md`, `VERSION`, or
`.claude-plugin/plugin.json`. Because each PR writes its own file, parallel PRs
never touch the same lines.

Name the file after your branch with the slash replaced by a dash, for example
`feature-handover-entries.md` for `feature/handover-entries`.

```markdown
---
bump: minor        # major | minor | patch (default patch)
section: Added     # heading for bullets that come before any ### heading
---
- **Short title.** What changed and why, written for someone updating a consumer project.

### Migration
- Anything a consumer must do after updating (optional).
```

CI fails a PR that adds no fragment, unless it is a release PR (one that changes
`VERSION`).

## Cutting a release

1. Branch `chore/release-X.Y.Z` from `main`.
2. Run `python3 scripts/release.py --dry-run` to preview, then `python3 scripts/release.py`.
   It picks the highest `bump` across the fragments, writes the new `CHANGELOG.md`
   section, bumps `VERSION` and `plugin.json`, and deletes the fragments.
3. Open the PR. When it merges, CI tags `vX.Y.Z` and consumer clones pick it up on
   their next `update.py` run.
