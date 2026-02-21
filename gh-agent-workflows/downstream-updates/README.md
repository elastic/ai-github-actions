# Downstream Updates Needed

Check downstream repositories in the `elastic` and `strawgate` orgs for workflow configuration drift and recommend updates.

## How it works

Reads `data/downstream-users.json` to discover downstream repositories, then inspects each repo's workflow files that reference `elastic/ai-github-actions`. For each workflow it compares the installed configuration against the canonical `example.yml` — checking permissions, version pins, triggers, and secrets — and reports per-repo drift in a filed issue.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/downstream-updates/example.yml \
  -o .github/workflows/downstream-updates.yml
```

See [example.yml](example.yml) for the full workflow file.

## Agentic Maintenance Required

This workflow emits expiring safe-outputs and needs the `agentics-maintenance` workflow to close expired reports. Install it once per repo:

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/.github/workflows/agentics-maintenance.yml \
  -o .github/workflows/agentics-maintenance.yml
```

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly (Monday) |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a downstream update report (max 1, auto-closes older reports, expires after 7 days)
