# Breaking Change Detector

Detect undocumented breaking changes in public interfaces.

## How it works

Scans recent commits (1-day lookback, 3-day on Mondays) for public interface or behavioral changes. Cross-references each commit against its PR description, changelog, and documentation before concluding a change is undocumented.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/breaking-change-detector/example.yml \
  -o .github/workflows/breaking-change-detector.yml
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

## Labeling and assigning created issues

The bundled [example.yml](example.yml) includes `workflow_dispatch` inputs `allowed-labels` and `allowed-assignees` that define which labels and assignees the agent may use when calling `create_issue`. These are passed into `additional-instructions` as allowlists — customize the defaults or provide your own `additional-instructions` to control labeling and assignment behavior.

## Safe Outputs

- `create-issue` — file a breaking change report (max 1, auto-closes older reports)
