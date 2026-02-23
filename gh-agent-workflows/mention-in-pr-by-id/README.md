# Mention in PR by ID

Trigger the PR assistant manually by PR number.

## How it works

Run via `workflow_dispatch` with a PR number and prompt text. The workflow invokes `mention-in-pr-by-id`, which hard-targets safe outputs to that PR.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-pr-by-id/example.yml \
  -o .github/workflows/mention-in-pr-by-id.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Inputs |
| --- | --- |
| `workflow_dispatch` | `pull-request-number`, `prompt` |

## Safe Outputs

- `add-comment` — reply on the targeted PR
- `create-pull-request-review-comment` — inline review comments on the targeted PR
- `submit-pull-request-review` — submit a review on the targeted PR
- `push-to-pull-request-branch` — push code changes to the targeted PR branch
- `resolve-pull-request-review-thread` — resolve threads on the targeted PR
