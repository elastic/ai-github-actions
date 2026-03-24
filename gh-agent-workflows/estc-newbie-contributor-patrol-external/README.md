# Newbie Contributor Patrol External (Elastic-specific)

Review docs from a new contributor perspective, cross-referencing published Elastic documentation.

## How it works

Like Newbie Contributor Patrol, but also cross-references the repo's documentation against published Elastic documentation on `elastic.co/docs`. Contradictions between the repo and published docs are treated as blocking issues.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-newbie-contributor-patrol-external/example.yml \
  -o .github/workflows/estc-newbie-contributor-patrol-external.yml
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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file an external new contributor docs review (max 1, auto-closes older reports)
