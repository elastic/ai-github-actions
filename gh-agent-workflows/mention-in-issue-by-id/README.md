# Mention in Issue by ID

Trigger the issue assistant manually by issue number.

## How it works

Run via `workflow_dispatch` with an issue number and prompt text. The workflow invokes `mention-in-issue-by-id`, which hard-targets safe issue comments to that issue.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-issue-by-id/example.yml \
  -o .github/workflows/mention-in-issue-by-id.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Inputs |
| --- | --- |
| `workflow_dispatch` | `issue-number`, `prompt` |

## Safe Outputs

- `add-comment` — reply on the targeted issue
- `create-pull-request` — open a PR with code changes
- `create-issue` — file a new issue
