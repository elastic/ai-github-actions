# CI Doctor

Investigate failed CI runs, identify root causes, and file actionable diagnosis issues.

## How it works

Triggers on failed `CI` workflow runs, inspects failed jobs and logs, checks for recurrence, and files one de-duplicated issue with concrete remediation steps.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/ci-doctor/example.yml \
  -o .github/workflows/ci-doctor.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `workflow_run` (`CI`) | On completion (job filters to failures) |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a CI diagnosis report (max 1, auto-closes older reports)
