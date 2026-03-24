# PR Actions Fixer

Opt-in fixer for failed PR checks that can push safe, targeted changes.

## How it works

Manually triggered with a specific failed workflow run ID. Reads the failed job logs, identifies the root cause, and pushes a targeted fix to the PR branch. Use this for opt-in repair of CI failures.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-actions-fixer/example.yml \
  -o .github/workflows/pr-actions-fixer.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Description |
| --- | --- |
| `workflow_dispatch` | Manual (requires a workflow run ID) |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `workflow-run-id` | Failed workflow run ID to analyze | Yes | — |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 1)
- `push-to-pull-request-branch` — push a fix to the PR branch
