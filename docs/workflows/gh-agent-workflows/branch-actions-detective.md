# Branch Actions Detective

Analyze failed branch CI runs and create or update a tracking issue.

Triggered automatically when a CI workflow fails on the default branch (for example, `main`) without an associated PR. It reads failed job logs, identifies the root cause, and files a deduplicated tracking issue with suggested remediation.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/branch-actions-detective/example.yml \
  -o .github/workflows/branch-actions-detective.yml
```

---

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `workflow_run` | `completed` | CI workflow failed on the default branch and the run has no associated PR |

!!! note
    The `workflows` list in the trigger must match the CI workflow names used by your repository.

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |
| `title-prefix` | Prefix used for created tracking issue titles | `[branch-actions-detective]` |

## Safe outputs

- `create-issue` — file a tracking issue for a new/distinct failure (max 1, auto-closes older matching issues)
- `noop` — emitted when no failed jobs are present or the failure is already tracked

## Example workflow

```yaml
name: Branch Actions Detective
on:
  workflow_run:
    workflows: ["Internal: CI", "CI", "Build", "Test"]
    types: [completed]

permissions:
  actions: read
  contents: read
  issues: write

jobs:
  run:
    if: >-
      github.event.workflow_run.conclusion == 'failure' &&
      github.event.workflow_run.head_branch == github.event.repository.default_branch &&
      toJSON(github.event.workflow_run.pull_requests) == '[]'
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-branch-actions-detective.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
