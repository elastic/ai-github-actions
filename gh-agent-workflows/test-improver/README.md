# Test Improver

Add focused tests for under-tested code and clean up redundant tests.

## How it works

Identifies code paths with no or minimal test coverage, adds focused tests that validate real behavior, and removes or consolidates clearly redundant tests. Only opens a PR for changes that would catch actual regressions — not trivial getters or incidental coverage. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-improver/example.yml \
  -o .github/workflows/test-improver.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-pull-request` — open a PR with test improvements
