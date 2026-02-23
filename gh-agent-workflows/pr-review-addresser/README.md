# PR Review Addresser

Auto-address PR review feedback — fix code, resolve threads, and push changes.

## How it works

Triggered when a pull request review is submitted with `changes_requested` or `commented` state. Reads the open review threads, makes targeted code fixes, runs tests, pushes changes to the PR branch, and resolves addressed threads. Uses judgment to decide whether to fix or explain — does not blindly accept every suggestion.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-review-addresser/example.yml \
  -o .github/workflows/pr-review-addresser.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `pull_request_review` | `submitted` | Review state is `changes_requested` or `commented`; PR is not draft; label `skip-auto-pr-review-addresser` is not present |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — reply to the PR conversation
- `push-to-pull-request-branch` — push code changes to the PR branch
- `resolve-pull-request-review-thread` — resolve review threads after addressing feedback
- `reply-to-pull-request-review-comment` — reply inline to specific review comment threads
