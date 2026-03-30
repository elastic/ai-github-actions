# PR Actions Detective

Analyze failed PR checks and report findings (read-only).

Triggered automatically when a CI workflow fails on a PR. Reads the failed job logs, identifies the root cause, and posts a comment with findings and recommended fixes. Read-only — never pushes changes.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-actions-detective/example.yml \
  -o .github/workflows/trigger-pr-actions-detective.yml
```

---

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `workflow_run` | `completed` | CI workflow failed and the run is associated with a PR |

!!! note
    The `workflows` list in the trigger must name the CI workflows you want the detective to monitor. Update it to match your repository's workflow names.

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | `github-actions[bot]` |

## Safe outputs

- `add-comment` — post a comment explaining the failure (max 1, hides older detective comments)
- `noop` — emitted when no failed jobs are found or diagnosis unchanged since last report

## Example workflow

```yaml
name: PR Actions Detective
on:
  workflow_run:
    workflows: ["CI", "Build", "Test"]
    types: [completed]

permissions:
  actions: read
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    if: >-
      github.event.workflow_run.conclusion == 'failure' &&
      toJSON(github.event.workflow_run.pull_requests) != '[]'
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-actions-detective.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
