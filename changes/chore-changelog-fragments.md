---
bump: minor
section: Added
---
- **Changelog fragments.** PRs now add one file under `changes/` instead of
  editing `VERSION`, `CHANGELOG.md`, and `plugin.json`, so parallel PRs no longer
  collide on the same lines. `scripts/release.py` compiles the fragments into a
  release on a `chore/release-X.Y.Z` branch, and CI fails a PR with no fragment.

### Changed
- **Clones follow release tags.** `update.py` now moves a clone forward to the
  latest `vX.Y.Z` tag instead of pulling the tip of `main`, and never moves a
  clone backwards. `--follow-main` restores the old behaviour; `.toolkit-pin`
  still wins over both.
- **`check_version.py` checks the release trio only.** `VERSION`, the latest
  `CHANGELOG.md` heading, and `plugin.json` must agree. The separate protocol
  version checks on the context files are gone; the protocol line itself is
  retired in 4.0.0.

### Migration
- Nothing to do in consumer projects. The next `update.py` run moves the clone
  from the `main` branch onto the latest release tag (a detached HEAD, which is
  expected).
