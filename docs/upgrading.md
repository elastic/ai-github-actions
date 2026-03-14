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

## Dedicated fixer removal (breaking)

Six dedicated fixer workflows have been removed. Any detector can now chain directly to `create-pr-from-issue` in the same workflow run, making these standalone fixers redundant.

### Removed workflows

| Removed workflow | Replacement |
| --- | --- |
| `gh-aw-bug-exterminator.lock.yml` | Chain Bug Hunter → `gh-aw-create-pr-from-issue.lock.yml` |
| `gh-aw-code-duplication-fixer.lock.yml` | Chain Code Duplication Detector → `gh-aw-create-pr-from-issue.lock.yml` |
| `gh-aw-text-beautifier.lock.yml` | Chain Text Auditor → `gh-aw-create-pr-from-issue.lock.yml` |
| `gh-aw-newbie-contributor-fixer.lock.yml` | Chain Newbie Contributor Patrol → `gh-aw-create-pr-from-issue.lock.yml` |
| `gh-aw-test-improver.lock.yml` | Chain Test Coverage Detector → `gh-aw-create-pr-from-issue.lock.yml` |
| `gh-aw-code-simplifier.lock.yml` | New Code Complexity Detector → `gh-aw-create-pr-from-issue.lock.yml` |

### Migration

Replace any `uses:` reference to a removed fixer with the chained pattern. For example, if you had separate Bug Hunter and Bug Exterminator workflows:

```yaml
# Before (two separate workflows)
# bug-hunter.yml — runs on schedule, creates issues
# bug-exterminator.yml — runs on schedule, picks up issues and creates PRs

# After (single chained workflow)
name: Bug Hunt & Fix
on:
  schedule:
    - cron: "0 11 * * 1-5"
  workflow_dispatch:

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  fix:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-create-pr-from-issue.lock.yml@v0
    with:
      target-issue-number: ${{ needs.detect.outputs.created_issue_number }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

See [Detector / Fixer Chaining](workflows/detector-fixer-chaining.md) for the full pattern and more examples.

### New workflow

- **Code Complexity Detector** — Scans source files for overly complex code (deep nesting, redundant conditionals, style outliers) and files a simplification report. Replaces the Code Simplifier. See [Code Complexity](workflows/gh-agent-workflows/code-complexity.md).

## v0.2.x → Latest (breaking changes)

- `stale-issues` was split: rename to `stale-issues-investigator` and add `stale-issues-remediator` if you want automatic objection handling + auto-close.
- Legacy workflow copies still exist for backwards compatibility only; downstream users should rename to the current workflow names now.

### Backwards-compatibility workflow copies (rename now)

- `gh-aw-breaking-change-detect.lock.yml` → `gh-aw-breaking-change-detector.lock.yml`
- `gh-aw-deep-research.lock.yml` → `gh-aw-internal-gemini-cli-web-search.lock.yml`
- `gh-aw-docs-drift.lock.yml` → `gh-aw-docs-patrol.lock.yml`
- `gh-aw-pr-ci-detective.lock.yml` → `gh-aw-pr-actions-detective.lock.yml`
- `gh-aw-estc-downstream-health.lock.yml` → `internal-downstream-health.lock.yml`
- `gh-aw-stale-issues.lock.yml` → `gh-aw-stale-issues-investigator.lock.yml`

### Example rename

```yaml
# Before
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues.lock.yml@v0

# After
uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues-investigator.lock.yml@v0
```
