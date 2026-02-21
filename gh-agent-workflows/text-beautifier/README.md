# Text Beautifier

Find typos, spelling errors, and unclear user-facing text and file a report issue.

## How it works

Scans user-facing text surfaces — error messages, CLI help text, log messages, and documentation strings — for typos, grammatical errors, unclear error messages, and inconsistent capitalization. Only reports text-only changes (no logic modifications), so findings are safe to apply without risk. The bar is high; most runs end with `noop` when text quality is already good.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-beautifier/example.yml \
  -o .github/workflows/text-beautifier.yml
```

See [example.yml](example.yml) for the full workflow file.

## Agentic Maintenance Required

This workflow emits expiring safe-outputs and needs the `agentics-maintenance` workflow to close expired reports. Install it once per repo:

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/.github/workflows/agentics-maintenance.yml \
  -o .github/workflows/agentics-maintenance.yml
````

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Mondays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a text quality report (max 1, auto-closes older reports)
