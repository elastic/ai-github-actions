# Code Duplication Detector

Analyze code for semantic function clustering and refactoring opportunities.

## How it works

Scans source files (by language or custom glob) to find semantically related functions that live in different files, duplicate implementations of the same logic, and functions that belong in a different module. Files a report with specific refactoring recommendations.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-detector/example.yml \
  -o .github/workflows/code-duplication-detector.yml
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
| `languages` | Comma-separated languages to analyze (ignored if `file-globs` is set) | No | `"go"` |
| `file-globs` | Comma-separated file globs to analyze (overrides `languages`) | No | `""` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Labeling and assigning created issues

The bundled [example.yml](example.yml) includes `workflow_dispatch` inputs `allowed-labels` and `allowed-assignees` that define which labels and assignees the agent may use when calling `create_issue`. These are passed into `additional-instructions` as allowlists — customize the defaults or provide your own `additional-instructions` to control labeling and assignment behavior.

## Safe Outputs

- `create-issue` — file a refactoring report (max 1, auto-closes older reports)
