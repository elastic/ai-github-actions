# Mention in PR

AI assistant for PRs — review, fix code, and push changes on demand.

## How it works

Activated by a comment on a pull request or inline review thread (the example trigger uses `/ai`, but the prefix is configurable). Reads the PR diff and codebase, then reviews code, answers questions, pushes fixes to the PR branch, or resolves review threads.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-pr/example.yml \
  -o .github/workflows/mention-in-pr.yml
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

## Safe Outputs

- `add-comment` — reply to the PR conversation
- `create-pull-request-review-comment` — inline review comments
- `submit-pull-request-review` — submit a review
- `push-to-pull-request-branch` — push code changes to the PR branch
- `resolve-pull-request-review-thread` — resolve review threads
