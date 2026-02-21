# Agent Deep Dive

Deep dive a specific agent workflow's recent runs to understand its behavior and surface detailed recommendations.

## How it works

Selects one agent workflow (by input or automatically rotated by day-of-week), downloads logs from its last 20 runs, extracts error snippets, traces tool call sequences, and files a detailed behavioral analysis issue. Focuses on one workflow at a time to provide depth rather than breadth.

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
| `target-workflow` | Workflow file name to deep dive (e.g. `trigger-pr-review.yml`). If empty, one is chosen automatically by rotating through workflows by day-of-week. | No | `""` |
| `run-count` | Number of recent runs to analyze | No | `20` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a deep dive report (max 1 open per run, expires after 14 days)
