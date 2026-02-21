# Text Auditor

Find typos, unclear error messages, and awkward user-facing text, then file an improvement issue.

## How it works

Scans user-facing text sources — CLI output, error messages, documentation, and help text — for typos, grammatical errors, unclear error messages, and inconsistent terminology. Files a single issue with concrete, low-effort fixes. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-auditor/example.yml \
  -o .github/workflows/text-auditor.yml
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
| `edit-typos` | How aggressively to flag typos and misspellings (`high`/`low`/`none`) | No | `low` |
| `edit-grammar` | How aggressively to flag grammar and sentence construction problems (`high`/`low`/`none`) | No | `low` |
| `edit-clarity` | How aggressively to flag unclear user-facing text (`high`/`low`/`none`) | No | `low` |
| `edit-terminology` | How aggressively to flag inconsistent terminology (`high`/`low`/`none`) | No | `low` |
| `edit-misleading-text` | How aggressively to flag text that conflicts with behavior (`high`/`low`/`none`) | No | `low` |
| `close-older-issues` | Whether to close older issues with the same title prefix when a new one is created | No | `true` |

### Edit Levels

Each edit dimension accepts one of three levels:

| Level | Meaning |
| --- | --- |
| `high` | Apply best judgment proactively within this dimension |
| `low` | Report only concrete, unambiguous problems in this dimension |
| `none` | Skip this dimension entirely |

## Safe Outputs

- `create-issue` — file a text improvement report (max 1, auto-closes older reports)
