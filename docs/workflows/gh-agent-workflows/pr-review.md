# PR Review

AI code review with inline comments on pull requests.

Reads the PR diff, repo conventions, and relevant source files. Posts inline review comments on specific changed lines with actionable feedback, then submits a review (approve, request changes, or comment) based on the configurable `intensity` level.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-review/example.yml \
  -o .github/workflows/trigger-pr-review.yml
```

---

## Trigger

| Event | Types |
| --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`, `unlabeled` |

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | `balanced` |
| `minimum_severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | `low` |

## Safe outputs

- `create-pull-request-review-comment` — inline review comments with code suggestions
- `submit-pull-request-review` — submit the review (approve, request changes, or comment)

## Example workflow

```yaml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review, labeled, unlabeled]

permissions:
  actions: read
  contents: read
  issues: write
  pull-requests: write

jobs:
  run:
    if: >-
      github.event.pull_request.draft == false &&
      !contains(github.event.pull_request.labels.*.name, 'skip-auto-pr-review')
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-review.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
