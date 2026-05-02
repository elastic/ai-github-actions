# Issue Fixer

Investigate new issues and provide actionable triage analysis. For straightforward fixes, implement and open a draft PR.

## How it works

Same as Issue Triage, but also implements the fix and opens a draft PR when the fix is straightforward and safe to land quickly.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-fixer/example.yml \
  -o .github/workflows/issue-fixer.yml
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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `COPILOT_GITHUB_TOKEN` | GitHub Copilot PAT for AI engine authentication | Yes |
| `EXTRA_COMMIT_GITHUB_TOKEN` | Token used to push an extra empty commit after PR creation to trigger CI checks. When omitted, CI is not re-triggered on the opened PR. | No |
| `GH_AW_GITHUB_TOKEN` | Ephemeral token (e.g. a GitHub App token) used for PR labeling safe outputs. When provided, labels applied by this workflow will trigger downstream label-based workflows. When omitted, the built-in `GITHUB_TOKEN` is used, which does not re-trigger other workflows. | No |

## Safe Outputs

- `add-comment` — post triage analysis on the issue
- `create-pull-request` — open a draft PR when a verified fix is implemented
