# Docs New Contributor Review External

Review docs from a new contributor perspective, cross-referencing against published Elastic documentation.

## How it works

Same as Docs New Contributor Review, but also cross-references the repo's documentation against published Elastic docs on `elastic.co/docs`, flagging contradictions that would block an external contributor.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-new-contributor-review-external/example.yml \
  -o .github/workflows/docs-new-contributor-review-external.yml
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
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a docs improvement report with external docs findings (max 1, auto-closes older reports)
