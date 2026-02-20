# Agent Efficiency

Analyze agent workflow logs for inefficiencies, errors, and prompt improvement opportunities.

## How it works

Reviews the last 3 days of agent workflow run logs, looking for recurring errors, tool call failures, and prompt patterns that lead to poor outcomes. Files an issue only when there is actionable evidence of systemic inefficiency.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/agent-efficiency/example.yml \
  -o .github/workflows/agent-efficiency.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file an efficiency report (max 1, auto-closes older reports)
