# PR Review

AI code review with inline comments on pull requests.

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
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | No | `balanced` |
| `minimum-severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | No | `low` |

## Safe Outputs

- `create-pull-request-review-comment` — inline review comments with code suggestions
- `submit-pull-request-review` — submit the review (approve, request changes, or comment)
