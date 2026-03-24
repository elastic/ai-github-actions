# Refactor Opportunist

Investigate the codebase as a senior architect, partially implement a refactor to prove viability, and pitch it via an issue.

## How it works

Reviews the codebase architecture, identifies structural pain points (tangled dependencies, duplicated patterns, inconsistent abstractions), and selects the highest-impact improvement. **Partially implements** the refactor on one representative slice to prove it works — running build, lint, and tests to verify viability — then files an issue with the proof-of-concept and an incremental rollout plan. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/refactor-opportunist/example.yml \
  -o .github/workflows/refactor-opportunist.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a refactor proposal with proof-of-concept (max 1, auto-closes older reports)
