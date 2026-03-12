# Detector / Fixer Chaining

Run a detector and its paired fixer so the fixer acts on the detector's findings immediately — no separate schedule needed.

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

There are two ways to chain a detector and fixer: **same-run chaining** and **dispatch chaining**. The recommended approach is dispatch chaining, which avoids artifact namespace conflicts.

## Dispatch chaining (recommended)

When a detector and fixer run as separate jobs inside the **same** workflow run, they share an uploaded-artifact namespace. This can cause artifact conflicts because both the detector and fixer workflows use identically named artifacts internally.

The workaround is to put the fix job into its own workflow file in your repo, so you have separate detect and fix workflows. The detect workflow dispatches the fix workflow after finding an issue, and because `workflow_dispatch` creates a **new** workflow run, each run gets its own artifact namespace.

You need two workflow files in `.github/workflows/`:

**Detect workflow** — runs on a schedule, dispatches the fix workflow when an issue is created:

```yaml
# .github/workflows/bug-hunt-detect.yml
name: Bug Hunt - Detect
on:
  schedule:
    - cron: "0 11 * * 1-5"
  workflow_dispatch:

permissions:
  actions: write
  contents: read
  issues: write
  pull-requests: read

jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  dispatch-fix:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'bug-hunt-fix.yml',
              ref: '${{ github.ref }}',
              inputs: {
                'issue-url': '${{ needs.detect.outputs.created_issue_url }}'
              }
            })
```

**Fix workflow** — triggered by dispatch with the issue URL as input:

```yaml
# .github/workflows/bug-hunt-fix.yml
name: Bug Hunt - Fix
on:
  workflow_dispatch:
    inputs:
      issue-url:
        description: "URL of the issue to fix"
        required: true

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  fix:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-exterminator.lock.yml@v0
    with:
      additional-instructions: |
        Focus on the bug described in ${{ inputs.issue-url }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

The detect workflow needs `actions: write` permission so it can dispatch the fix workflow. The fix workflow runs in its own workflow run with a clean artifact namespace.

## Same-run chaining

> **Note:** Same-run chaining places the detector and fixer in a single workflow run. This can cause artifact namespace conflicts because both jobs upload artifacts with the same names. Use [dispatch chaining](#dispatch-chaining-recommended) if you hit this issue.

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

### Audit creates issue -> create PR in same workflow

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

### Bug Hunter + Bug Exterminator (dispatch)

**`.github/workflows/bug-hunt-detect.yml`**

```yaml
name: Bug Hunt - Detect
on:
  schedule:
    - cron: "0 11 * * 1-5"
  workflow_dispatch:

permissions:
  actions: write
  contents: read
  issues: write
  pull-requests: read

jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  dispatch-fix:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'bug-hunt-fix.yml',
              ref: '${{ github.ref }}',
              inputs: {
                'issue-url': '${{ needs.detect.outputs.created_issue_url }}'
              }
            })
```

**`.github/workflows/bug-hunt-fix.yml`**

```yaml
name: Bug Hunt - Fix
on:
  workflow_dispatch:
    inputs:
      issue-url:
        description: "URL of the issue to fix"
        required: true

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  fix:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-exterminator.lock.yml@v0
    with:
      additional-instructions: |
        Focus on the bug described in ${{ inputs.issue-url }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

### Code Duplication Detector + Code Duplication Fixer (dispatch)

**`.github/workflows/code-duplication-detect.yml`**

```yaml
name: Code Duplication - Detect
on:
  schedule:
    - cron: "0 12 * * 1-5"
  workflow_dispatch:

permissions:
  actions: write
  contents: read
  issues: write
  pull-requests: read

jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-duplication-detector.lock.yml@v0
    with:
      languages: TypeScript, JavaScript
      file-globs: "src/**/*.ts, src/**/*.js"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  dispatch-fix:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'code-duplication-fix.yml',
              ref: '${{ github.ref }}',
              inputs: {
                'issue-url': '${{ needs.detect.outputs.created_issue_url }}'
              }
            })
```

**`.github/workflows/code-duplication-fix.yml`**

```yaml
name: Code Duplication - Fix
on:
  workflow_dispatch:
    inputs:
      issue-url:
        description: "URL of the issue to fix"
        required: true

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  fix:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-duplication-fixer.lock.yml@v0
    with:
      additional-instructions: |
        Focus on the duplication described in ${{ inputs.issue-url }}
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

### Bug Hunter + Bug Exterminator (same-run)

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

### Code Duplication Detector + Code Duplication Fixer (same-run)

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
| **Dispatch chaining** (two workflows) | Recommended — fully autonomous detect-then-fix with no artifact conflicts |
| **Same-run chaining** (single workflow) | Simpler setup but may hit artifact namespace conflicts |
| **Separate schedules** | Human-in-the-loop review — run the detector, review its issues, then let the fixer run later |
| **Detector only** | When you only want reports, not automatic fixes |

## Notes

- The fixer job's `if` condition prevents it from running when the detector finds nothing (noop).
- Both jobs share the same `COPILOT_GITHUB_TOKEN` secret.
- For same-run chaining, the caller workflow needs the union of both workflows' permissions (e.g., `contents: write` + `pull-requests: write` for the fixer).
- For dispatch chaining, the detect workflow needs `actions: write` so it can trigger the fix workflow. The fix workflow sets its own permissions independently.
- Chaining does not replace the standalone examples — you can still run each workflow independently.
