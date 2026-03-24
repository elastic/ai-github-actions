# Test Coverage Detector

Find under-tested code paths and file a test coverage report.

## How it works

Identifies code paths with no or minimal test coverage by running coverage tools (when available) and analyzing recent changes for missing tests. Files a report with specific, actionable recommendations for each gap — including the user scenario and suggested test approach. The bar is high; most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-coverage-detector/example.yml \
  -o .github/workflows/test-coverage-detector.yml
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

- `create-issue` — file a test coverage report (max 1, auto-closes older reports)

## Pairing

This detector finds test coverage gaps. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) to automatically fix findings.
