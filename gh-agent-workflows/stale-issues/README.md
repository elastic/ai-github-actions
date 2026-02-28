# Stale Issues

Find open issues that appear to already be resolved, label them as `stale`, and automatically close them after a 30-day grace period.

## How it works

The workflow runs in two phases on every invocation:

1. **Close phase** — Issues labeled with the configured stale label are checked for objections (comments like "not stale" or "still relevant"); if found, the label is removed via the `remove-labels` safe output. Otherwise, issues that have carried the label for 30+ days are automatically closed. Maintainers can also remove the label at any time during the grace period to prevent closure.
2. **Tag phase** — The agent investigates open issues for evidence of resolution (linked PRs, code evidence, conversation consensus). Newly identified candidates are labeled and included in a summary report issue.

A scripted prep step runs before the agent starts, dumping all stale-labeled issues and their recent comments to `/tmp/stale-labeled-issues.json` and `/tmp/stale-recent-comments.json`. This gives the agent deterministic inputs and avoids redundant API calls.

## Investigation strategy

The agent starts with high-signal candidates (linked PRs, resolution language in comments, and long-stale updates) and includes coverage stats in no-op runs (total open issues, candidate count, analyzed count).

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues/example.yml \
  -o .github/workflows/stale-issues.yml
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
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `stale-label` | Label used to mark stale issues | No | `stale` |

## Safe Outputs

- `create-issue` — file a stale issues report (max 1, auto-closes older reports)
- `add-labels` — apply the stale label to issues identified as likely resolved
- `remove-labels` — remove the stale label when a fresh objection indicates an issue is still active
- `close-issue` — close issues that have been labeled stale for 30+ days
