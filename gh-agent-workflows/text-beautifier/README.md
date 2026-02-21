# Text Beautifier

Find typos, unclear error messages, and awkward user-facing text, then file an improvement issue.

## How it works

Scans user-facing text sources — CLI output, error messages, documentation, and help text — for typos, grammatical errors, unclear error messages, and inconsistent terminology. Files a single issue with concrete, low-effort fixes. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-beautifier/example.yml \
  -o .github/workflows/text-beautifier.yml
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

- `create-issue` — file a text improvement report (max 1, auto-closes older reports)
