# Detector / Fixer Chaining

Run a detector and a fixer in a **single workflow run**, so findings are acted on immediately — no separate schedule needed.

## Why chain?

When a detector runs on its own schedule, it creates an issue via `github-actions[bot]`. GitHub does not trigger other workflows from events created by `github-actions[bot]`, so a fixer must poll on its own schedule. Chaining removes that delay: the fixer job reads the detector's output directly and runs in the same workflow.

## How it works

The gh-aw compiler exposes safe-output results as `workflow_call` outputs. A detector that creates an issue will output:

| Output | Description |
|---|---|
| `created_issue_number` | Number of the first created issue |
| `created_issue_url` | URL of the first created issue |

Your caller workflow chains a detector to `create-pr-from-issue` with `needs` and `if`:

```yaml
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

The fix job only runs when the detector actually created an issue. The generic `create-pr-from-issue` workflow reads the issue body and implements a fix, so any detector can chain to it without a dedicated fixer workflow.

## Complete examples

### Bug Hunter → Create PR from Issue

```yaml
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

### Code Duplication Detector → Create PR from Issue

```yaml
name: Code Duplication Detect & Fix
on:
  schedule:
    - cron: "0 12 * * 1-5"
  workflow_dispatch:

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-duplication-detector.lock.yml@v0
    with:
      languages: "go,python,typescript"
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

### Text Auditor → Create PR from Issue

```yaml
name: Text Audit & Fix
on:
  schedule:
    - cron: "0 13 * * 1-5"
  workflow_dispatch:

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-text-auditor.lock.yml@v0
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

Each detector directory includes an `example-chained.yml` you can copy directly.

## When to chain vs. separate schedules

| Approach | Best for |
|---|---|
| **Chained** (single run) | Fully autonomous loops where you want immediate action on findings |
| **Detector only** | Human-in-the-loop review — run the detector, review its issues, then manually fix or assign |
| **Detector + separate `create-pr-from-issue`** | When you want a human to review issues before the fixer runs on its own schedule |

## Notes

- The fix job's `if` condition prevents it from running when the detector finds nothing (noop).
- Both jobs share the same `COPILOT_GITHUB_TOKEN` secret.
- The caller workflow needs the union of both workflows' permissions (e.g., `contents: write` + `pull-requests: write` for the fixer).
- Chaining does not replace the standalone examples — you can still run each workflow independently.
- Any detector that uses the `create-issue` safe output can chain to `create-pr-from-issue`.
