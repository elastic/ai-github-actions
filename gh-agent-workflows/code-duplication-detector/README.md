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

If you want detector-to-fixer handoff via labels, add these optional `workflow_dispatch` inputs to your local workflow copy and reference them from `additional-instructions`:

| Option | Description (with usage tips) | Suggested default |
| --- | --- | --- |
| `allowed-labels` | Comma-separated labels the agent is allowed to apply when it calls `create_issue`. Tip: include both a detector label and your handoff label (for example `ai:fix-ready`) so Issue Fixer can trigger from a labeled issue. Leave empty to skip labeling. | `code-duplication,ai:fix-ready` |
| `allowed-assignees` | Comma-separated GitHub usernames the agent is allowed to assign on created issues. Tip: keep this list small so assignment stays predictable. Leave empty to skip assigning. | `""` |

## Safe Outputs

- `create-issue` — file a refactoring report (max 1, auto-closes older reports)
