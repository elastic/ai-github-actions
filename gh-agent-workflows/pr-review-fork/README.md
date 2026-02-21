# PR Review (Fork)

AI code review with inline comments on pull requests, including pull requests from forks.

## ⚠️ Security Warning

> **Only use this workflow on private repositories, or on public repositories where every contributor is explicitly trusted.**

This workflow uses the [`pull_request_target`](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#pull_request_target) trigger so that it runs in the context of the *base* repository. This grants the workflow access to repository secrets — which is what allows it to review pull requests from forks.

**Risks on public repositories:**

- `pull_request_target` grants access to secrets even for untrusted forks.
- If you add `setup-commands` that check out or execute code from the pull request, a malicious contributor could exfiltrate your secrets.
- The agent itself does **not** check out PR code (it reads the diff via the GitHub API), so it is safe in the default configuration. Any `setup-commands` that run fork code break that guarantee.

For public repositories, use the standard [pr-review](../pr-review/README.md) workflow instead, which uses the `pull_request` trigger and never has access to secrets on fork PRs. Maintainers will need to manually approve the first workflow run for new contributors.

## How it works

Reads the PR diff, repo conventions, and relevant source files. Posts inline review comments on specific changed lines with actionable feedback, then submits a review (approve, request changes, or comment) based on the configurable `intensity` level.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-review-fork/example.yml \
  -o .github/workflows/pr-review-fork.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `pull_request_target` | `opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`, `unlabeled` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts — **do not run fork code here** | No | `""` |
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | No | `balanced` |
| `minimum_severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | No | `low` |

## Safe Outputs

- `create-pull-request-review-comment` — inline review comments with code suggestions
- `submit-pull-request-review` — submit the review (approve, request changes, or comment)
