# Agent Efficiency

Analyze agent workflow logs for excessive tool calls, errors, failures, and bad agent behavior.

## How it works

Reviews the last 3 days of agent workflow run logs, documenting recurring errors, excessive tool calls, early failures, and bad agent behavior patterns. Includes a per-repository summary with exact date ranges and run counts. Reports on what is happening and when — not on suggested fixes or impact assessments.

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
