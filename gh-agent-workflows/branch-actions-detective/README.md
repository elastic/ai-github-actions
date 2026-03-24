# Branch Actions Detective

Analyze failed branch CI runs and create or update a tracking issue.

## How it works

Triggered automatically when a CI workflow fails on a protected branch (e.g. `main`) without an associated PR. Reads the failed job logs, identifies the root cause, and creates an issue with findings and recommended fixes. Repeated failures for the same root cause are deduplicated — existing issues are left open and no duplicate is filed.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/branch-actions-detective/example.yml \
  -o .github/workflows/branch-actions-detective.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `workflow_run` | `completed` | CI workflow failed on the default branch with no associated PR |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a tracking issue for the CI failure (max 1, auto-closes older issues)
- `noop` — emitted when no failed jobs are found or failure already tracked by an open issue
