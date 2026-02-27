# PR Buildkite Detective (Elastic-specific)

Analyze failed PR checks backed by Buildkite and report findings (read-only).

## How it works

Triggered automatically when a commit status or check run reports a failure. Looks up the related Buildkite build via MCP, analyzes failed jobs/logs/annotations, and posts a comment with root cause and recommended fixes. Read-only — never pushes changes.

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
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `buildkite-org` | Buildkite organization slug | No | `elastic` |
| `buildkite-pipeline` | Buildkite pipeline slug (auto-discovered if not provided) | No | `""` |

## Required Secrets

- `COPILOT_GITHUB_TOKEN`
- `BUILDKITE_API_TOKEN` *(optional — omit for public pipelines; the workflow will fetch logs from public Buildkite build pages instead)*

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 3)
