# Buildkite Flaky Test Reporter (Elastic-specific)

Collect flaky tests from the Buildkite Test Engine and file per-test GitHub issues; add a follow-up comment when a previously reported test is still flaky.

## How it works

Runs on a weekly schedule (or on demand). Queries the Buildkite Test Engine REST API for tests flagged as flaky across one or more test suites, then for each flaky test either opens a new tracking issue or adds a comment to the existing open issue saying the test is still flaky. Duplicate suppression is based on open issue search. Read-only except for issue creation and comments.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-buildkite-flaky-test-reporter/example.yml \
  -o .github/workflows/estc-buildkite-flaky-test-reporter.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Condition |
| --- | --- |
| `schedule` | Every Monday at 09:00 UTC |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `buildkite-organization-slug` | Buildkite organization slug | No | GitHub org name |
| `buildkite-test-suite-slugs` | Space-separated list of test suite slugs to scan | No | All suites |
| `min-occurrences` | Minimum flaky occurrences to report a test | No | `2` |
| `issue-label` | Label applied to created issues (must exist in the repo) | No | `flaky-test` |

## Required Secrets

- `COPILOT_GITHUB_TOKEN`
- `BUILDKITE_API_TOKEN`

## Safe Outputs

- `create-issue` — open a new tracking issue per flaky test (max 20 per run, expires after 30 days)
- `add-comment` — comment on an existing issue when the test is still flaky (max 20 per run)
- `noop` — emitted when no flaky tests meet the threshold or all are already tracked
