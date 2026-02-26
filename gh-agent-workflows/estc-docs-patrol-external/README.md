# Estc Docs Patrol External

Detect code changes that require updates to published Elastic documentation, `applies_to` tags, or backports.

## How it works

Like Docs Patrol, but focuses on changes that require updates to published Elastic documentation on `elastic.co/docs`. Also flags features that need `applies_to` tag updates or documentation backports to earlier release branches.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-docs-patrol-external/example.yml \
  -o .github/workflows/estc-docs-patrol-external.yml
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

- `create-issue` — file an external docs patrol report (max 1, auto-closes older reports)
