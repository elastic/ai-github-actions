# Mention in Issue

AI assistant for issues — answer questions, debug, and create PRs on demand.

Activated by a comment on an issue (the example trigger uses `/ai`, but the prefix is configurable). Reads the issue context and codebase, then answers questions, debugs problems, suggests solutions, or opens a PR with a proposed fix.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-issue/example.yml \
  -o .github/workflows/trigger-mention-in-issue.yml
```

---

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on an issue (not a PR); the example trigger filters on `/ai` prefix |

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |

## Safe outputs

- `add-comment` — reply to the issue
- `create-pull-request` — open a PR with code changes
- `create-issue` — file a new issue

## Example workflow

```yaml
name: Mention in Issue
on:
  issue_comment:
    types: [created]

permissions:
  actions: read
  contents: write
  discussions: write
  issues: write
  pull-requests: write

jobs:
  run:
    if: >-
      github.event.issue.pull_request == null &&
      startsWith(github.event.comment.body, '/ai')
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-mention-in-issue.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
