# Mention in PR (no sandbox)

AI assistant for PRs — review, fix code, and push changes on demand. The agent sandbox is disabled, allowing direct Docker access.

## How it works

Activated by a comment on a pull request or inline review thread (the example trigger uses `/ai`, but the prefix is configurable). Reads the PR diff and codebase, then reviews code, answers questions, pushes fixes to the PR branch, or resolves review threads.

This variant runs **without the agent sandbox** (`sandbox.agent: false`), which means the agent has direct access to the Docker daemon. Use this when your `setup-commands` need to build or run Docker containers.

> ⚠️ **Security note**: Disabling the agent sandbox removes the network firewall and filesystem isolation that the sandboxed variant provides. Use only when Docker access is required.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-pr-no-sandbox/example.yml \
  -o .github/workflows/mention-in-pr-no-sandbox.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on a PR; the example trigger filters on `/ai` prefix |
| `pull_request_review_comment` | `created` | Inline review comment; the example trigger filters on `/ai` prefix |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `draft-prs` | Whether to create pull requests as drafts | No | `true` |

## Safe Outputs

- `add-comment` — reply to the PR conversation
- `create-pull-request-review-comment` — inline review comments
- `submit-pull-request-review` — submit a review
- `push-to-pull-request-branch` — push code changes to the PR branch
- `create-pull-request` — create a new PR with changes (used for fork PRs where pushing is not possible)
- `resolve-pull-request-review-thread` — resolve review threads
