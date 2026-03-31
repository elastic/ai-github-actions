# PR Buildkite Detective (Elastic-specific)

Analyze failed Buildkite PR checks and report findings (read-only).

Triggered by failed `status` and `check_run` events that contain a Buildkite build URL. The workflow fetches failed Buildkite script job logs (including recursively triggered child builds), analyzes likely root cause, and posts a focused remediation comment on the PR.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-pr-buildkite-detective/example.yml \
  -o .github/workflows/estc-pr-buildkite-detective.yml
```

---

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `status` | N/A | Commit status changed to `failure` |
| `check_run` | `completed` | Check run completed with conclusion `failure` |

The example trigger applies this gate:

```yaml
if: >-
  (github.event_name == 'status' && github.event.state == 'failure') ||
  (github.event_name == 'check_run' && github.event.check_run.conclusion == 'failure')
```

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |

## Required secrets

- `COPILOT_GITHUB_TOKEN`
- `BUILDKITE_API_TOKEN`

## Behavior notes

- Resolves Buildkite context from `target_url`/`details_url` in the incoming GitHub event.
- Fetches Buildkite failed script jobs with recursive traversal of trigger jobs (`collect_failed_jobs`), so downstream failed child pipelines are included.
- Skips early (notice + exit) when:
  - the build is not associated with a PR
  - build state is not `failed` or `failing`
  - no failed script jobs are present
- Proceeds only when failed script jobs are found, writes summaries/log tails under `/tmp/gh-aw/`, and analyzes those logs.
- Performs deduplication against the latest prior detective comment; emits `noop` instead of a duplicate diagnosis.

## Safe outputs

- `add-comment` — post a PR comment with root cause and remediation (max 1, older detective comments hidden)
- `noop` — emitted when:
  - the agent starts but Buildkite failure data is unavailable, or
  - diagnosis is unchanged from the most recent detective report

## Example workflow

```yaml
name: Estc PR Buildkite Detective
on:
  status:
  check_run:
    types: [completed]

permissions:
  actions: read
  contents: read
  discussions: write
  issues: write
  pull-requests: write

jobs:
  run:
    if: >-
      (github.event_name == 'status' && github.event.state == 'failure') ||
      (github.event_name == 'check_run' && github.event.check_run.conclusion == 'failure')
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-estc-pr-buildkite-detective.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
      BUILDKITE_API_TOKEN: ${{ secrets.BUILDKITE_API_TOKEN }}
```
