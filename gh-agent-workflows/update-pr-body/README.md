# Update PR Body

Keep pull request bodies in sync with the code changes on every commit.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/update-pr-body/example.yml \
  -o .github/workflows/update-pr-body.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review` | PR is not a draft |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actors (comma-separated usernames) | No | `github-actions[bot]` |

## Safe Outputs

- `update-pull-request` — update the PR body when significant drift is detected
