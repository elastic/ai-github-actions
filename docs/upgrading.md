# Upgrading

> **Migrating from Claude Workflows?** See the [Migration Guide](migration-guide.md) for step-by-step instructions on migrating from legacy Claude Composite Actions to GitHub Agent Workflows.

## Stale issues split

### Workflow rename

The `stale-issues` workflow has been renamed to `stale-issues-investigator` and its remediation features have been split into a new companion workflow, `stale-issues-remediator`. A backwards-compatibility copy is provided for the old name and will be removed in a future release.

| Old name | New name | Compat copy? |
| --- | --- | --- |
| `stale-issues` | `stale-issues-investigator` | Yes |

**How to update:** In your trigger workflow file, change the `uses:` line:

```yaml
# Before
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues.lock.yml@v0

# After
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues-investigator.lock.yml@v0
```

### New workflow — Stale Issues Remediator

The remediation phase (objection handling, 30-day auto-close) is now a separate workflow: `stale-issues-remediator`. Install it alongside the investigator for a fully autonomous stale-issue lifecycle.

### All backwards-compatibility copies

These old workflow names are maintained as full file copies with a deprecation header. They will be removed in a future release — migrate to the new names now.

| Old name | New name | Since |
| --- | --- | --- |
| `breaking-change-detect` | `breaking-change-detector` | v0.2.6 |
| `docs-drift` | `docs-patrol` | v0.2.6 |
| `pr-ci-detective` | `pr-actions-detective` | v0.2.6 |
| `test-improvement` | `test-improver` | v0.2.6 |
| `stale-issues` | `stale-issues-investigator` | v0.2.7 |

---

## v0.2.5 → v0.2.6

### Breaking changes — workflow renames

The following workflows have been renamed. Consumers referencing the old `uses:` path must update their trigger files. Temporary backwards-compatibility copies are provided for the four most widely adopted workflows (marked below); the rest require a manual rename. The compatibility copies include a deprecation header and will be removed in a future release — migrate to the new names now.

| Old name | New name | Compat copy? |
| --- | --- | --- |
| `breaking-change-detect` | `breaking-change-detector` | Yes |
| `docs-drift` | `docs-patrol` | Yes |
| `pr-ci-detective` | `pr-actions-detective` | Yes |
| `test-improvement` | `test-improver` | Yes |
| `docs-new-contributor-review` | `newbie-contributor-patrol` | No |
| `flaky-test-triage` | `flaky-test-investigator` | No |
| `issue-triage-pr` | `issue-fixer` | No |
| `pr-ci-fixer` | `pr-actions-fixer` | No |
| `semantic-function-clustering` | `code-duplication-detector` | No |
| `address-pr-feedback` | `pr-review-addresser` | No |

**How to update:** In your trigger workflow file, change the `uses:` line:

```yaml
# Before
uses: elastic/ai-github-actions/.github/workflows/gh-aw-docs-drift.lock.yml@v0

# After
uses: elastic/ai-github-actions/.github/workflows/gh-aw-docs-patrol.lock.yml@v0
```

### Breaking changes — removed workflows

| Workflow | Replacement |
| --- | --- |
| `pr-checks-fix` | Use `pr-actions-fixer` instead (manual `workflow_dispatch` trigger) |

### Permission changes

The following workflows have updated permissions. If you copied the original `example.yml`, update your trigger file to match.

| Workflow | Change |
| --- | --- |
| `pr-actions-detective` (was `pr-ci-detective`) | Removed `discussions: write`; changed `pull-requests: write` → `pull-requests: read` |
| `pr-actions-fixer` (was `pr-ci-fixer`) | Removed `discussions: write` |
| `issue-triage` | Added `actions: read` |
| `mention-in-issue` | Added `actions: read` |
| `mention-in-pr` | Added `actions: read` |

### Other changes

- All workflows now accept a `model` input (default: `gpt-5.3-codex`) to select the AI model.
- All workflows now accept `setup-commands`, `allowed-bot-users`, and `messages-footer` inputs.
- Switched to upstream `github/gh-aw` compiler (v0.48.1).
- New shared fragments: `scheduled-audit.md` and `scheduled-fix.md` for building custom detector/fixer workflows.

### Migration checklist

1. [ ] Update renamed workflow `uses:` paths in your trigger files
2. [ ] Update permissions to match the new examples (see table above)
3. [ ] Remove any `pr-checks-fix` trigger (replace with `pr-actions-fixer` if needed)
4. [ ] Optionally adopt new workflows (`text-auditor`, `code-duplication-fixer`, etc.)
5. [ ] Test by running `workflow_dispatch` on updated triggers
