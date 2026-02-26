# Mention in Issue

AI assistant for issues — answer questions, debug, and create PRs on demand.

## How it works

Activated by a comment on an issue (the example trigger uses `/ai`, but the prefix is configurable). Reads the issue context and codebase, then answers questions, debugs problems, suggests solutions, or opens a PR with a proposed fix.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-issue/example.yml \
  -o .github/workflows/mention-in-issue.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on an issue (not a PR); the example trigger filters on `/ai` prefix |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — reply to the issue
- `create-pull-request` — open a PR with code changes
- `create-issue` — file a new issue
- `add-labels` — add labels to the issue or another issue/PR
- `assign-to-user` — assign the issue or another issue to a specific user
- `add-reviewer` — add a reviewer to a pull request
