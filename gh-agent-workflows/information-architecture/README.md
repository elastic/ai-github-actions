# Information Architecture

Audit the application's UI information architecture for navigation, placement, and consistency issues.

## How it works

Traces the component tree from the top-level App/Layout component, examining navigation structure, action placement, picker positioning, data presentation, progressive disclosure, grouping, consistency, and empty states. Only files an issue when a concrete, user-impacting IA problem is found — something a real user would likely get confused or frustrated by; most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/information-architecture/example.yml \
  -o .github/workflows/information-architecture.yml
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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file an information architecture report (max 1)
