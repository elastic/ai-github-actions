# CLI Consistency Checker

Inspect `gh-aw` CLI help surfaces for inconsistencies, typos, and documentation drift.

## How it works

Runs the CLI help entry points, compares wording and command coverage against docs, and files a consolidated issue only when it finds concrete inconsistencies.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/cli-consistency-checker/example.yml \
  -o .github/workflows/cli-consistency-checker.yml
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

- `create-issue` — file a CLI consistency report (max 1, auto-closes older reports)
