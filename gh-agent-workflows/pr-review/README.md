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

## Fork Support

To review pull requests from forked repositories, use the `pull_request_target` variant:

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-review/example-fork.yml \
  -o .github/workflows/pr-review.yml
```

> [!WARNING]
> **Private repositories only.** `pull_request_target` runs in the base repository context and exposes repository secrets to fork-triggered runs. On public repositories, any external contributor can open a fork PR and trigger expensive API calls or attempt prompt injection. Use the standard `pull_request` trigger for public repos — GitHub's fork approval gate ensures the workflow only runs for trusted contributors.

See [example-fork.yml](example-fork.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`, `unlabeled` |
| `pull_request_target` (fork support) | `opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`, `unlabeled` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | No | `balanced` |
| `minimum-severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | No | `low` |

## Safe Outputs

- `create-pull-request-review-comment` — inline review comments with code suggestions
- `submit-pull-request-review` — submit the review (approve, request changes, or comment)
