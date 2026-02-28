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

## Labeling created issues

The bundled [example.yml](example.yml) includes `workflow_dispatch` inputs named `issue-labels` and `assign-to`, then passes them into `additional-instructions` so created issues can be labeled (for example, `breaking-change,ai:fix-ready`) and optionally assigned (for example, `octocat` or `copilot`).
These are instruction-level hints (not create-issue safe-output policy settings), so the agent still chooses whether to include them when calling `create_issue`.

## Safe Outputs

- `create-issue` — file a breaking change report (max 1, auto-closes older reports)
