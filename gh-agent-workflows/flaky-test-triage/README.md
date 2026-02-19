# Flaky Test Triage

Investigate flaky tests using open issues and failed CI runs, then file a single triage report issue with root-cause-first recommendations.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/flaky-test-triage/example.yml \
  -o .github/workflows/flaky-test-triage.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Condition |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |
| `workflow_run` | CI workflow failed and run is associated with a PR |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |

## Safe Outputs

- `create-issue` — file one flaky-test triage report issue (auto-closes older triage reports)
