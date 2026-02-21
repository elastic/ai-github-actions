# Docs Patrol

Detect code changes that require documentation updates and file issues.

## How it works

Scans recent commits (7-day lookback by default) for public API or behavioral changes not reflected in nearby documentation. Checks READMEs, contribution guides, and other discovered markdown files before filing.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-patrol/example.yml \
  -o .github/workflows/docs-patrol.yml
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
| `lookback-window` | Git lookback window for detecting recent commits (e.g. `7 days ago`, `14 days ago`) | No | `"7 days ago"` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a docs patrol report (max 1, auto-closes older reports)
