# Mention in Issue

AI assistant for issues — answer questions, debug, and create PRs via `/ai`.

## How it works

Responds to `/ai <request>` comments on issues. Can read code, run commands, answer questions, suggest solutions, or open a PR with a proposed fix.

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
| `issue_comment` | `created` | Comment starts with `/ai` and is on an issue (not a PR) |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |

## Safe Outputs

- `add-comment` — reply to the issue
- `create-pull-request` — open a PR with code changes
- `create-issue` — file a new issue
