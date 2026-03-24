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

## Detector creates issue -> assign to Copilot

Instead of chaining to a fixer workflow, you can assign the created issue to GitHub's Copilot coding agent and let it open a PR. This is useful when you don't have a dedicated fixer workflow or want to use Copilot's native implementation flow.

```yaml
jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  assign-to-copilot:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Assign issue to Copilot
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh issue edit ${{ needs.detect.outputs.created_issue_number }} \
            --repo ${{ github.repository }} \
            --add-assignee @copilot
```

Copilot picks up the assignment, reads the issue, and opens a PR — using its own session and context window. No `COPILOT_GITHUB_TOKEN` is needed for the handoff job itself since assignment only requires `issues: write`.

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

Most detector directories include an `example-chained.yml` you can copy directly. For detectors without one, follow the pattern above.

## When to chain vs. separate schedules

| Approach | Best for |
|---|---|
| **Chained** (single run) | Fully autonomous loops where you want immediate action on findings |
| **Assign to Copilot** | Lightweight handoff — detector creates the issue, Copilot implements it natively |
| **Detector only** | Human-in-the-loop review — run the detector, review its issues, then manually fix or assign |

## Notes

- The fix job's `if` condition prevents it from running when the detector finds nothing (noop).
- Both jobs share the same `COPILOT_GITHUB_TOKEN` secret.
- The caller workflow needs the union of both workflows' permissions (e.g., `contents: write` + `pull-requests: write` for the fixer).
- Chaining does not replace the standalone examples — you can still run each workflow independently.
- Any detector that uses the `create-issue` safe output can chain to `create-pr-from-issue`.
- For comment-only responses (e.g., triage summaries, implementation guidance without opening a PR), chain to [Create Comment On Issue](gh-agent-workflows/create-comment-on-issue.md) instead.
