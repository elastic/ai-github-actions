# Code Duplication Fixer

Fix code-duplication-detector issues by consolidating duplicate functions and opening a focused PR.

## How it works

Picks up open issues filed by the Code Duplication Detector (labeled `refactor` or with `[refactor]` in the title), selects one well-scoped finding, refactors the duplicate or misplaced code, runs tests, and opens a PR. Only acts on safe, behavior-preserving refactors. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-fixer/example.yml \
  -o .github/workflows/code-duplication-fixer.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-pull-request` — open a PR with the refactor (max 1)

## Pairing

This workflow is the read-write companion to [Code Duplication Detector](../code-duplication-detector/). The detector finds issues; the fixer consolidates the duplicates.
