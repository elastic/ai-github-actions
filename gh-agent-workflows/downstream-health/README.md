# Downstream Health

Monitor downstream repositories using AI workflows and report quality issues.

## How it works

Discovers elastic-owned repositories that use ai-github-actions workflows, monitors recent agent activity (comments and PR reviews by `github-actions[bot]`), and reports when agents are silent or producing unexpected outputs.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/downstream-health/example.yml \
  -o .github/workflows/downstream-health.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Daily |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a downstream health report (max 1, auto-closes older reports)
