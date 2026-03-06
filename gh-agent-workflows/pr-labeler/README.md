# PR Labeler

Evaluate pull requests and apply one classification label from a configurable label set.

## How it works

Triggered by PR activity. The workflow ensures classification labels exist, runs the PR Labeler agent, and applies exactly one label from the configured list while removing conflicting labels from the same list.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-labeler/example.yml \
  -o .github/workflows/pr-labeler.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review`, `edited` |

## Configuration

Set `CLASSIFICATION_LABELS` in the trigger workflow to a comma-separated list:

```yaml
env:
  CLASSIFICATION_LABELS: "human_required,no_human_required"
```

You can also pass `additional-instructions` to define custom semantics for your labels.

The workflow enforces label choice primarily through the agent prompt. Provide explicit semantics in `additional-instructions` so the agent can map PR risk to your label set reliably.

## Human vs no-human example

```yaml
env:
  CLASSIFICATION_LABELS: "human_required,no_human_required"

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-labeler.lock.yml@v0
    with:
      classification-labels: ${{ env.CLASSIFICATION_LABELS }}
      additional-instructions: |
        Use `human_required` when the PR is high-risk, broad, or uncertain.
        Use `no_human_required` only for straightforward, low-risk changes.
        Only use labels from `human_required,no_human_required`.
```

## Safe Outputs

- `add-labels` — apply one classification label to the PR
- `remove-labels` — remove conflicting classification labels from the configured set
