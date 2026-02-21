# Newbie Contributor Patrol

Review docs from a new contributor perspective and file high-impact issues.

## How it works

Reads all contributor-facing documentation (README, CONTRIBUTING, DEVELOPING, etc.) as if it were a new contributor's first encounter with the project. Follows getting-started paths, checks for missing prerequisites, and flags blocking gaps. Only files issues for high-impact problems; most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example.yml \
  -o .github/workflows/newbie-contributor-patrol.yml
```

See [example.yml](example.yml) for the full workflow file.

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
| `close-older-issues` | Whether to close older issues with the same title prefix when a new one is created | No | `true` |

## Safe Outputs

- `create-issue` — file a new contributor docs review (max 1, auto-closes older reports)

## Pairing

This workflow is the detector half. Pair with [Newbie Contributor Fixer](../newbie-contributor-fixer/) to automatically fix the issues it finds.
