# Log Searching Agent

Search workflow logs for specific terms and investigate matches to surface recurring patterns and actionable issues.

## How it works

A preflight step downloads workflow run logs for a configurable time window, searches them for caller-supplied terms (exact match), and writes the results to disk. The agent then analyzes the search results — looking for recurring patterns, frequency trends, and root causes — and files a triage issue when actionable findings exist.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/log-searching-agent/example.yml \
  -o .github/workflows/log-searching-agent.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Description |
| --- | --- |
| `workflow_dispatch` | Manual (requires workflow name and search terms) |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `workflow` | Workflow file name to search logs for (e.g. `ci.yml`) | Yes | — |
| `search-terms` | Comma-separated list of exact match search terms | Yes | — |
| `days` | Number of days to look back for workflow runs | No | `7` |
| `max-runs` | Maximum number of runs to download logs from | No | `20` |
| `conclusion` | Filter runs by conclusion (`failure`, `success`, `cancelled`, `any`) | No | `failure` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `title-prefix` | Title prefix for created issues | No | `[log-search]` |

## Safe Outputs

- `create-issue` — file a log search investigation report (max 1, auto-closes older reports)
