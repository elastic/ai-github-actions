# Mention in PR

AI assistant for PRs — review, fix code, and push changes on demand.

Activated by a comment on a pull request or inline review thread (the example trigger uses `/ai`, but the prefix is configurable). Reads the PR diff and codebase, then reviews code, answers questions, pushes fixes to the PR branch, or resolves review threads.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-pr/example.yml \
  -o .github/workflows/trigger-mention-in-pr.yml
```

---

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on a PR; the example trigger filters on `/ai` prefix |
| `pull_request_review_comment` | `created` | Inline review comment; the example trigger filters on `/ai` prefix |

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |
| `report-failure-as-issue` | When `true`, agent failures are reported as a GitHub issue | `true` |
| `github-token-policy` | **Elastic-specific.** Backstage TokenPolicy id for `elastic/oblt-actions/github/create-token`. When set, mint an OIDC ephemeral GitHub token in each token-consuming job so comments, reviews, and pushes re-trigger downstream workflows (and can satisfy CODEOWNERS when the Vault app is listed). Requires Elastic TokenPolicy / ephemeral-token infrastructure; leave empty outside Elastic. The caller job must grant `id-token: write`. | `""` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `GH_AW_GITHUB_TOKEN` | Optional override token for GitHub API writes. Prefer `github-token-policy` with OIDC when available. When neither is set, `GITHUB_TOKEN` is used. | No |

## Safe outputs

- `add-comment` — reply to the PR conversation
- `create-pull-request-review-comment` — inline review comments
- `submit-pull-request-review` — submit a review
- `push-to-pull-request-branch` — push code changes to the PR branch
- `resolve-pull-request-review-thread` — resolve review threads

## Example workflow

```yaml
name: Mention in PR
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  actions: read
  contents: write
  discussions: write
  issues: write
  pull-requests: write
  id-token: write

jobs:
  run:
    if: >-
      startsWith(github.event.comment.body, '/ai') &&
      (github.event.issue.pull_request != null || github.event_name == 'pull_request_review_comment')
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-mention-in-pr.lock.yml@v0
    # with:
      # Elastic-specific (OIDC): github-token-policy: "<shared-token-policy-id>"
      # Requires Elastic TokenPolicy / ephemeral-token infrastructure; leave unset outside Elastic.
```
