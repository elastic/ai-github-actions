# Docs New Contributor Review

Review docs from a new contributor perspective and file high-impact issues.

## How it works

Simulates the onboarding experience of a first-time contributor — reading setup docs and following the quick-start path as far as possible without secrets or admin privileges. Only files an issue for **high-impact** blockers (missing steps, broken commands, undocumented prerequisites).

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-new-contributor-review/example.yml \
  -o .github/workflows/docs-new-contributor-review.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a docs improvement report (max 1, auto-closes older reports)
