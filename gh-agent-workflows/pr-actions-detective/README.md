# PR Actions Detective

Analyze failed PR checks and report findings (read-only).

## How it works

Triggered automatically when a CI workflow fails on a PR. Reads the failed job logs, identifies the root cause, and posts a comment with findings and recommended fixes. Read-only — never pushes changes.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-actions-detective/example.yml \
  -o .github/workflows/pr-actions-detective.yml
````

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
