# Agent Suggestions

Suggest new agent workflows based on software development needs and downstream activity.

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

## Safe Outputs

- `create-issue` — file an agent suggestions report (max 1, auto-closes older reports)
