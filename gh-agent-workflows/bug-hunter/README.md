# Bug Hunter

Find a reproducible, user-impacting bug and file a report issue.

## How it works

Reviews 28 days of git history for user-facing changes that could introduce bugs. For each candidate, writes a **new** minimal reproduction script and runs it — filing a report only when the bug is concretely confirmed. The bar is high; most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-hunter/example.yml \
  -o .github/workflows/bug-hunter.yml
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

- `create-issue` — file a bug report (max 1, auto-closes older reports)
