# Upgrading

> **Migrating from Claude Workflows?** See the [Migration Guide](migration-guide.md) for step-by-step instructions on migrating from legacy Claude Composite Actions to GitHub Agent Workflows.

## gh-aw compiler v0.51.0

Compiler upgrade with new features and bug fixes. No breaking changes — recompile your workflows to pick up improvements.

### New features

- **Workflow outputs from safe-outputs** — Detector workflows now expose `created_issue_number` and `created_issue_url` as `workflow_call` outputs. Fixer workflows expose `created_pr_number` and `created_pr_url`. This enables [detector/fixer chaining](workflows/detector-fixer-chaining.md) in a single action run.
- **Agent failure issues auto-labeled** — Issues created on agent failure are automatically tagged with the `agentic-workflows` label.
- **Guard policies** — New guard policy configuration with schema validation (adopt when you define policies).
- **MCP Gateway tuning** — `payloadPathPrefix` and `payloadSizeThreshold` settings available for fine-grained MCP gateway control.

### Bug fixes

- Checkout `token` field corrected (`checkout.github-token` → `checkout.token`)
- Activation job `/tmp/gh-aw` directory reliably created before writing `aw_info.json`
- Emoji ZWJ sequences no longer trigger false positives in the unicode-abuse scanner
- MCP gateway config validation fixed (undeclared `payloadSizeThreshold` field removed)
- Missing `cross-repo` and `auth` properties restored to safe output schemas
- Activation job `contents: read` permission added
- Report template headers normalized to `h3+` levels

## gh-aw compiler v0.56.2 (approx)

Compiler updates in this range fix safe-output workflow-call output propagation so detector/audit workflows reliably expose created issue outputs (for example, `created_issue_number`).

That enables same-run chaining patterns like:
- detector/audit job creates an issue
- caller checks `if: needs.run.outputs.created_issue_number != ''`
- caller immediately starts `gh-aw-create-pr-from-issue`

## v0.2.x → Latest (breaking changes)

- `stale-issues` was split: rename to `stale-issues-investigator` and add `stale-issues-remediator` if you want automatic objection handling + auto-close.
- Legacy workflow copies still exist for backwards compatibility only; downstream users should rename to the current workflow names now.

### Backwards-compatibility workflow copies (rename now)

- `gh-aw-breaking-change-detect.lock.yml` → `gh-aw-breaking-change-detector.lock.yml`
- `gh-aw-deep-research.lock.yml` → `gh-aw-internal-gemini-cli-web-search.lock.yml`
- `gh-aw-docs-drift.lock.yml` → `gh-aw-docs-patrol.lock.yml`
- `gh-aw-pr-ci-detective.lock.yml` → `gh-aw-pr-actions-detective.lock.yml`
- `gh-aw-test-improvement.lock.yml` → `gh-aw-test-improver.lock.yml`
- `gh-aw-estc-downstream-health.lock.yml` → `internal-downstream-health.lock.yml`
- `gh-aw-stale-issues.lock.yml` → `gh-aw-stale-issues-investigator.lock.yml`

### Example rename

```yaml
# Before
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues.lock.yml@v0

# After
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues-investigator.lock.yml@v0
```
