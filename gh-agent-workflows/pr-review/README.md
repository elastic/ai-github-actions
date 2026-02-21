# PR Review

AI code review with inline comments on pull requests.

## How it works

Reads the PR diff, repo conventions, and relevant source files. Posts inline review comments on specific changed lines with actionable feedback, then submits a review (approve, request changes, or comment) based on the configurable `intensity` level.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-review/example.yml \
  -o .github/workflows/pr-review.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`, `unlabeled` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | No | `balanced` |
| `minimum-severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | No | `low` |

## Minimize resolved review threads

The example workflow includes [minimize-resolved-pr-reviews](https://github.com/strawgate/minimize-resolved-pr-reviews) as a second job that runs after every review. It collapses resolved threads, keeping PR conversations focused. This requires `pull-requests: write` permissions (already included in the example).

## Safe Outputs

- `create-pull-request-review-comment` — inline review comments with code suggestions
- `submit-pull-request-review` — submit the review (approve, request changes, or comment)
