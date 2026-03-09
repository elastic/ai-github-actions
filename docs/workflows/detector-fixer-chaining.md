# Detector / Fixer Chaining

Run a detector and its paired fixer in a **single workflow run**, so the fixer acts on the detector's findings immediately — no separate schedule needed.

## Why chain?

When a detector and fixer run on separate schedules, the detector creates an issue via `github-actions[bot]`. GitHub does not trigger other workflows from events created by `github-actions[bot]`, so the fixer must poll on its own schedule. Chaining removes that delay: the fixer job reads the detector's output directly.

## How it works

The gh-aw compiler (v0.51.0+) exposes safe-output results as `workflow_call` outputs. A detector that creates an issue will output:

| Output | Description |
|---|---|
| `created_issue_number` | Number of the first created issue |
| `created_issue_url` | URL of the first created issue |

A fixer that creates a PR will output:

| Output | Description |
|---|---|
| `created_pr_number` | Number of the first created pull request |
| `created_pr_url` | URL of the first created pull request |

Your caller workflow chains them with `needs` and `if`:

```yaml
jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  fix:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-exterminator.lock.yml@v0
    with:
      additional-instructions: |
        Focus on the bug described in ${{ needs.detect.outputs.created_issue_url }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

The fixer job only runs when the detector actually created an issue.

## Audit creates issue -> create PR in same workflow

With current compiler output propagation, you can chain directly from an audit/detector workflow to `gh-aw-create-pr-from-issue` in the same run:

```yaml
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-text-auditor.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  create_pr_from_issue:
    needs: run
    if: needs.run.outputs.created_issue_number != ''
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-create-pr-from-issue.lock.yml@v0
    with:
      target-issue-number: ${{ needs.run.outputs.created_issue_number }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

This pattern gives you: **Audit creates issue -> same workflow: if issue was created, then start `create-pr-from-issue`**.

## Complete examples

### Bug Hunter + Bug Exterminator

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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-exterminator.lock.yml@v0
    with:
      additional-instructions: |
        Focus on the bug described in ${{ needs.detect.outputs.created_issue_url }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

### Code Duplication Detector + Code Duplication Fixer

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
      languages: TypeScript, JavaScript
      file-globs: "src/**/*.ts, src/**/*.js"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  fix:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-duplication-fixer.lock.yml@v0
    with:
      additional-instructions: |
        Focus on the duplication described in ${{ needs.detect.outputs.created_issue_url }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

## When to chain vs. separate schedules

| Approach | Best for |
|---|---|
| **Chained** (single run) | Fully autonomous loops where you want immediate action on findings |
| **Separate schedules** | Human-in-the-loop review — run the detector, review its issues, then let the fixer run later |
| **Detector only** | When you only want reports, not automatic fixes |

## Notes

- The fixer job's `if` condition prevents it from running when the detector finds nothing (noop).
- Both jobs share the same `COPILOT_GITHUB_TOKEN` secret.
- The caller workflow needs the union of both workflows' permissions (e.g., `contents: write` + `pull-requests: write` for the fixer).
- Chaining does not replace the standalone examples — you can still run each workflow independently.
