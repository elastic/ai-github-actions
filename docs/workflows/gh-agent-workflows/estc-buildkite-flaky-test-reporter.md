# Buildkite Flaky Test Reporter (Elastic-specific)

Collect flaky tests from the Buildkite Test Engine and file per-test GitHub issues; add a follow-up comment when a previously reported test is still flaky.

Runs on a weekly schedule (or on demand). Queries the Buildkite Test Engine REST API for tests flagged as flaky across one or more test suites, then for each flaky test either opens a new tracking issue or adds a comment to the existing open issue. Duplicate suppression is based on open issue search.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-buildkite-flaky-test-reporter/example.yml \
  -o .github/workflows/estc-buildkite-flaky-test-reporter.yml
```

---

## Trigger

| Event | Condition |
| --- | --- |
| `schedule` | Every Monday at 09:00 UTC |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |
| `buildkite-organization-slug` | Buildkite organization slug | GitHub org name |
| `buildkite-test-suite-slugs` | Space-separated list of test suite slugs to scan | All suites |
| `min-occurrences` | Minimum flaky occurrences required to report a test | `2` |
| `issue-label` | Label applied to created issues (must already exist in the repo) | `flaky-test` |

## Required secrets

- `COPILOT_GITHUB_TOKEN`
- `BUILDKITE_API_TOKEN`

## Safe outputs

- `create-issue` — open a new tracking issue per flaky test (max 20 per run, expires after 30 days)
- `add-comment` — comment on an existing issue when the test is still flaky (max 20 per run)
- `noop` — emitted when no flaky tests meet the threshold or all are already tracked

## Example workflow

```yaml
name: Buildkite Flaky Test Reporter
on:
  schedule:
    - cron: "0 9 * * 1"  # every Monday at 09:00 UTC
  workflow_dispatch:

permissions:
  actions: read
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-estc-buildkite-flaky-test-reporter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
      BUILDKITE_API_TOKEN: ${{ secrets.BUILDKITE_API_TOKEN }}
    # with:
    #   buildkite-organization-slug: "my-org"
    #   buildkite-test-suite-slugs: "suite-a suite-b"
    #   min-occurrences: 2
    #   issue-label: "flaky-test"
```
