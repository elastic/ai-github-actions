# Agent Efficiency

Analyze agent workflow logs for inefficiencies, errors, and prompt improvement opportunities.

## How it works

Downloads logs from the last 7 days of failed agent workflow runs, extracts error snippets, and analyzes agent behavior patterns — excessive tool calls, wrong tool usage, instruction violations, and recurring errors. Files an issue with a per-repo run summary and observations about observed behavior. Does not include suggested fixes or impact assessments.

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
