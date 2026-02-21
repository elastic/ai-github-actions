# Terminal Stylist

Find low-risk text and terminal UX improvements for user-facing CLI output.

## How it works

Scans user-facing output strings, formatting calls, and terminal presentation patterns to find typos, inconsistent wording, and readability improvements, then files a single issue with low-impact fixes.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/terminal-stylist/example.yml \
  -o .github/workflows/terminal-stylist.yml
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

- `create-issue` — file a terminal/text quality report (max 1, auto-closes older reports)
