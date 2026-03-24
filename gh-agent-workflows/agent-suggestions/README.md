# Agent Suggestions

Suggest new agent workflows based on software development needs and downstream activity.

## How it works

Inventories existing workflows, reviews open issues and PRs for recurring unmet needs, and checks the activity of downstream users. Suggests new workflows that would fill clear gaps — and only files a report when there are high-confidence, non-duplicate suggestions.

## Quick Install

    mkdir -p .github/workflows && curl -sL \
      https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/agent-suggestions/example.yml \
      -o .github/workflows/agent-suggestions.yml

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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file an agent suggestions report (max 1, auto-closes older reports)
