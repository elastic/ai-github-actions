# PR Labeler

Evaluate pull requests and apply one classification label from a configurable label set.

## How it works

Triggered by PR activity. The workflow runs the PR Labeler agent, applies exactly one label from the configured list, and removes conflicting labels from that same list.

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
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review` |

## Configuration

Set `classification-labels` in the trigger workflow as a comma-separated list:

```yaml
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-labeler.lock.yml@v0
    with:
      classification-labels: "human_required,no_human_required"
```

You can also pass `additional-instructions` to define custom semantics for your labels.
Ensure the labels already exist in your repository.

The workflow enforces label choice primarily through the agent prompt. Provide explicit semantics in `additional-instructions` so the agent can map PR risk to your label set reliably.

## Human vs no-human example

```yaml
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-labeler.lock.yml@v0
    with:
      classification-labels: "human_required,no_human_required"
      additional-instructions: |
        Use `human_required` when the PR is high-risk, broad, or uncertain.
        Use `no_human_required` only for straightforward, low-risk changes.
        Only use labels from `human_required,no_human_required`.
```

## Safe Outputs

- `add-labels` — apply one classification label to the PR
- `remove-labels` — remove conflicting classification labels from the configured set
