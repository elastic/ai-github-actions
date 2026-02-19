# PR CI Detective

Analyze failed PR checks and report findings (read-only).

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-ci-detective/example.yml \
  -o .github/workflows/pr-ci-detective.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `workflow_run` | `completed` | CI workflow failed and the run is associated with a PR |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 3)
