# Dependency Review

Analyze Dependabot and Renovate PRs across dependency types, with deeper checks for GitHub Actions and Buildkite updates.

## How it works

Triggered when Dependabot or Renovate opens or updates a PR. Classifies each dependency update type, applies shared checks (changelog, usage compatibility, and testability), and runs extra checks for GitHub Actions commit verification and Buildkite pin-format risk. Posts a structured analysis comment and optionally labels the PR `needs-human-review` or `higher-risk`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/dependency-review/example.yml \
  -o .github/workflows/dependency-review.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened` | PR author is `dependabot[bot]` or `renovate[bot]` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — post an analysis comment on the PR (max 1)
- `add-labels` — label the PR when human review or higher risk is detected (max 3)

## Manual usage with mention-in-pr

You can also analyze any dependency update PR on demand using `mention-in-pr`. Comment on the PR with:

```
/ai Analyze this dependency update PR across dependency types: classify each update, run applicable risk checks, summarize changelog highlights, and note testability in PR context.
```
