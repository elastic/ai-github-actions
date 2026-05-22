# Issue Triage

Investigate new issues and provide actionable triage analysis.

## How it works

When a new issue is opened, reads the issue and related code, reproduces or validates the report where possible, and posts a comment with a root cause analysis and actionable next steps.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-triage/example.yml \
  -o .github/workflows/issue-triage.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `issues` | `opened` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt. | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `COPILOT_GITHUB_TOKEN` | GitHub Copilot PAT for AI engine authentication | Yes |
| `GH_AW_GITHUB_TOKEN` | Ephemeral token (e.g. a GitHub App token) used for issue labeling safe outputs. When provided, labels applied by this workflow will trigger downstream label-based workflows. When omitted, the built-in `GITHUB_TOKEN` is used, which does not re-trigger other workflows. | No |

## Safe Outputs

- `add-comment` — post a triage analysis comment on the issue
