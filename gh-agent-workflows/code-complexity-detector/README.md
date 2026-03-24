# Code Complexity Detector

Find overly complex code and file a simplification report.

## How it works

Scans source files (by language or custom glob) for overly complex code — deep nesting, redundant conditionals, style outliers, and inline logic that reimplements existing helpers. Files a report with specific simplification recommendations.

## Quick Install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-complexity-detector/example.yml \
  -o .github/workflows/code-complexity-detector.yml
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
| `severity-threshold` | Minimum severity to include (`high`, `medium`, `low`) | No | `"medium"` |
| `title-prefix` | Title prefix for created issues | No | `"[complexity]"` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a complexity report (max 1, expires after 7 days)

## Pairing

This detector finds complexity hotspots. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) to automatically fix findings.
