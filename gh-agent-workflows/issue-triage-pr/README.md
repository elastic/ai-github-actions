# Issue Triage (with PR)

Investigate new issues and provide actionable triage analysis. For straightforward fixes, implement and open a draft PR.

## How it works

Same as Issue Triage, but also implements the fix and opens a draft PR when the fix is straightforward and safe to land quickly.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-triage-pr/example.yml \
  -o .github/workflows/issue-triage-pr.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `issues` | `opened` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — post triage analysis on the issue
- `create-pull-request` — open a draft PR when a verified fix is implemented
