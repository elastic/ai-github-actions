# PR Labeler

Evaluate pull requests and apply one or more classification labels from a configurable label set.

## How it works

Triggered by PR activity. The workflow runs the PR Labeler agent and applies labels from the configured list.

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
`classification-labels` is required.
Ensure the labels already exist in your repository.

The workflow enforces label choice primarily through the agent prompt. Provide explicit semantics in `additional-instructions` so the agent can map PR risk to your label set reliably.

## Holistic risk rubric (recommended)

When defining custom labels, map them to a consistent multi-factor risk model:

- **Change scope**: how broad/cross-cutting the change is
- **Criticality**: whether changes touch security/auth, CI/workflows, runtime-critical paths, or data/schema integrity
- **Reversibility**: how safe/easy rollback is
- **Verification confidence**: strength of tests and validation evidence
- **Operational safeguards**: canary/feature-flag/staged rollout/rollback readiness

Practical guidance:

- Large or additive PRs are not automatically highest risk.
- Escalate to highest risk only with concrete high-blast-radius signals.
- If evidence is ambiguous, classify one level more conservatively.

## Example semantics (optional)

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

- `add-labels` — apply one or more classification labels to the PR
- `remove-labels` — remove outdated/conflicting classification labels from the configured set
