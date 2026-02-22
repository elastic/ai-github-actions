# UX Design Patrol

Detect UI/UX design drift in recent commits and file a consolidation report.

## How it works

Scans recent commits (7-day lookback by default) for user-facing patterns that duplicate or conflict with patterns already established elsewhere in the codebase. Checks output formatting, prompts, CLI flags, status representations, help text, and other user-visible elements before filing a low-noise, high-signal consolidation report.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/ux-design-patrol/example.yml \
  -o .github/workflows/ux-design-patrol.yml
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

- `create-issue` — file a UX design drift report (max 1, auto-closes older reports)
