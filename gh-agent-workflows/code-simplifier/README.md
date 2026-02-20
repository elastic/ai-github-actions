# Code Simplifier

Simplify overcomplicated code with high-confidence refactors.

## How it works

Scans the codebase for overcomplicated patterns: deep nesting, redundant conditionals, dead code, and manual re-implementations of standard library functions. Only opens a PR for changes that are **provably** behavior-preserving and obvious at a glance — a reviewer should not have to think hard to approve it. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-simplifier/example.yml \
  -o .github/workflows/code-simplifier.yml
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

- `create-pull-request` — open a PR with simplification changes
