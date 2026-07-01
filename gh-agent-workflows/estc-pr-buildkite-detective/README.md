# PR Buildkite Detective (Elastic-specific)

Analyze failed PR checks backed by Buildkite and report findings (read-only).

## How it works

Triggered automatically when a commit status or check run reports a failure. Uses `BUILDKITE_API_TOKEN` to fetch failed job logs from the Buildkite REST API, then analyzes the logs and posts a PR comment with root cause and recommended fixes. Read-only — never pushes changes.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-pr-buildkite-detective/example.yml \
  -o .github/workflows/estc-pr-buildkite-detective.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `status` | N/A | Commit status changed to `failure` |
| `check_run` | `completed` | Check run completed with conclusion `failure` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `report-failure-as-issue` | When `true`, agent failures are reported as a GitHub issue | No | `true` |

## Required Secrets

- `BUILDKITE_API_TOKEN`

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 1 per run); uses `reply_to_id` to update the existing detective comment in place when one is found
- `noop` — emitted when diagnosis is unchanged since the last report

If the agent starts but the pre-fetched Buildkite summary is unavailable, it emits `noop` (`No Buildkite failure data`). If no failed script jobs are found (or the build is not a PR build / not in a failed state), the workflow exits early with a notice and does not emit `noop`.

## Comment Lifecycle

The workflow keeps **at most one detective comment** per PR:

- **Same diagnosis**: the agent emits `noop` and the existing comment is left untouched.
- **New diagnosis**: the agent finds the existing detective comment (identified by the `<!-- gh-aw-detective: estc-pr-buildkite-detective -->` marker) and updates it in place via `reply_to_id`. If no previous comment exists, a new one is created.
