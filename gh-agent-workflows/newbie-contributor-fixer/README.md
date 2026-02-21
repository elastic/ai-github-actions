# Newbie Contributor Fixer

Fix newbie-contributor-patrol issues by improving documentation and opening a focused PR.

## How it works

Picks up open issues filed by the Newbie Contributor Patrol (labeled `newbie-contributor` or with `[newbie-contributor]` in the title), applies the suggested documentation improvements, and opens a PR. Focuses on filling gaps in the contributor onboarding path — missing prerequisites, broken commands, undocumented requirements. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-fixer/example.yml \
  -o .github/workflows/newbie-contributor-fixer.yml
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

- `create-pull-request` — open a PR with documentation fixes (max 1)

## Pairing

This workflow is the fixer half. Pair with [Newbie Contributor Patrol](../newbie-contributor-patrol/) to detect the issues it fixes.
