# PR Buildkite Detective

Analyze failed PR checks backed by Buildkite and report findings (read-only).

## How it works

Triggered automatically when a CI workflow fails on a PR. Looks up the related Buildkite build via MCP, analyzes failed jobs/logs/annotations, and posts a comment with root cause and recommended fixes. Read-only — never pushes changes.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-buildkite-detective/example.yml \
  -o .github/workflows/pr-buildkite-detective.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `workflow_run` | `completed` | CI workflow failed and the run is associated with a PR |

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
- `BUILDKITE_API_TOKEN`

## Safe Outputs

- `add-comment` — post a comment explaining the failure (max 3)

> Note: due workflow editing guardrails, this change adds the shim source under `github/workflows/`. A maintainer must relocate it to `.github/workflows/` before release.
