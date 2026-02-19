# PR CI Fixer

Opt-in fixer for failed PR checks that can push safe, targeted changes.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-ci-fixer/example.yml \
  -o .github/workflows/pr-ci-fixer.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Description |
| --- | --- |
| `workflow_dispatch` | Manual (requires a workflow run ID) |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `workflow-run-id` | Failed workflow run ID to analyze | Yes | — |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 3)
- `push-to-pull-request-branch` — push a fix to the PR branch
