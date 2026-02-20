# PR Checks Fix

Analyze failed PR checks and optionally push fixes.

## How it works

Triggered automatically when a CI workflow fails on a PR. Reads the failed job logs, identifies the root cause, and pushes a targeted fix to the PR branch. Posts a comment explaining the failure whether or not a fix was applied.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-checks-fix/example.yml \
  -o .github/workflows/pr-checks-fix.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `workflow_run` | `completed` | CI workflow failed and the run is associated with a PR |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 3)
- `push-to-pull-request-branch` — push a fix to the PR branch
