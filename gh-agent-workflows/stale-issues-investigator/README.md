# Stale Issues Investigator

Find open issues that appear to already be resolved, label them as `stale`, and file a report.

## How it works

The agent investigates open issues for evidence of resolution (linked PRs, code evidence, conversation consensus). Newly identified candidates are labeled with the configured stale label and included in a summary report issue.

## Investigation strategy

A prescan step fetches up to 500 open issues (sorted by least recently updated) into a local index file before the agent starts, giving it an immediate view of the most likely stale candidates. The agent then starts with high-signal candidates (linked PRs, resolution language in comments, and long-stale updates) and includes coverage stats in no-op runs (total open issues, candidate count, analyzed count).

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues-investigator/example.yml \
  -o .github/workflows/stale-issues-investigator.yml
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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `stale-label` | Label used to mark stale issues | No | `stale` |

## Safe Outputs

- `create-issue` — file a stale issues report (max 1, auto-closes older reports)
- `add-labels` — apply the stale label to issues identified as likely resolved

## Pairing

This workflow is the investigation companion to [Stale Issues Remediator](../stale-issues-remediator/). The investigator finds and labels stale candidates; the remediator handles objections and closes expired ones. Install both for a fully autonomous stale-issue lifecycle, or use the investigator alone for human-in-the-loop review.
