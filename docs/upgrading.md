# Upgrading

> **Migrating from Claude Workflows?** See the [Migration Guide](migration-guide.md) for step-by-step instructions on migrating from legacy Claude Composite Actions to GitHub Agent Workflows.

## v0.2.x → Latest (breaking changes)

- `stale-issues` was split: rename to `stale-issues-investigator` and add `stale-issues-remediator` if you want automatic objection handling + auto-close.
- Legacy workflow copies still exist for backwards compatibility only; downstream users should rename to the current workflow names now.

### Backwards-compatibility workflow copies (rename now)

- `gh-aw-breaking-change-detect.lock.yml` → `gh-aw-breaking-change-detector.lock.yml`
- `gh-aw-docs-drift.lock.yml` → `gh-aw-docs-patrol.lock.yml`
- `gh-aw-pr-ci-detective.lock.yml` → `gh-aw-pr-actions-detective.lock.yml`
- `gh-aw-test-improvement.lock.yml` → `gh-aw-test-improver.lock.yml`
- `gh-aw-stale-issues.lock.yml` → `gh-aw-stale-issues-investigator.lock.yml`

### Example rename

```yaml
# Before
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues.lock.yml@v0

# After
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues-investigator.lock.yml@v0
```
