# Autonomy Atomicity Analyzer

Find patterns that block concurrent development by multiple agents or developers.

## How it works

Scans the project structure for autonomy and atomicity blockers: global mutable state that forces serial edits, manual routing registries that are merge-conflict magnets, god files with disproportionate import fan-in/fan-out, over-broad tests that break on any change, implicit ordering dependencies, and shared configuration hotspots. Only files an issue when a concrete, actionable blocker is found; most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/autonomy-atomicity-analyzer/example.yml \
  -o .github/workflows/autonomy-atomicity-analyzer.yml
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

- `create-issue` — file an autonomy/atomicity blocker report (max 1)
