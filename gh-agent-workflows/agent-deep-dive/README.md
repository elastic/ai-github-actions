# Agent Deep Dive

Deep-dive analysis of a single agent workflow's runs to understand behavior and provide in-depth recommendations.

## How it works

Each run rotates through the available agent workflows using the current ISO week number, analyzing a different agent each week. For the selected agent, it downloads and analyzes ALL runs from the last 14 days (not just failures), examining tool call patterns, error rates, output quality, and timing. It then files an issue with a detailed report and specific, data-backed recommendations.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/agent-deep-dive/example.yml \
  -o .github/workflows/agent-deep-dive.yml
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

- `create-issue` — file a deep-dive report for the selected agent (max 1, auto-closes older reports, expires after 14 days)
