# Plan

Create actionable implementation plans from issue comments and optionally split work into new issues/sub-issues.

## How it works

Activated by a comment on an issue (the example trigger uses `/plan`). The workflow investigates the issue and codebase, posts a triage-style plan comment, and can create follow-up issues (including sub-issues via `parent`) when decomposition is useful.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/plan/example.yml \
  -o .github/workflows/plan.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on an issue (not a PR); the example trigger filters on `/plan` prefix |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — post the plan summary on the issue
- `create-issue` — file follow-up issues and sub-issues
