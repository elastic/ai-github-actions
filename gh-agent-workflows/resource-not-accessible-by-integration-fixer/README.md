# Resource Not Accessible By Integration Fixer

Daily fixer that scans for `Resource not accessible by integration` errors across long-term branches and opens remediation PRs.

## How it works

Runs once every 24 hours. Queries all failed workflow runs from the last 24 hours on the default branch and any configured long-term (release) branches. For each run, it downloads the logs and searches for the exact error text `Resource not accessible by integration`. Matching runs are grouped by workflow file, and the agent opens **one PR per affected workflow** that patches the missing permissions using the centralized remediation instructions from the observability-cicd repository. If no matching failures are found the run ends with `noop` and no PR is opened.

Each generated PR:
- includes links to all matching failed runs, a verbatim log excerpt, root cause, and the remediation applied;
- requests review from the `elastic/observablt-ci` team;
- is left open (never auto-merged) until approved.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/resource-not-accessible-by-integration-fixer/example.yml \
  -o .github/workflows/resource-not-accessible-by-integration-fixer.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Daily (06:00 UTC) |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `long-term-branches` | Space-separated list of long-term branch names to scan in addition to the default branch (e.g. `'8.x 7.17'`) | No | `""` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `draft-prs` | Whether to create pull requests as drafts | No | `false` |

## Safe Outputs

- `create-pull-request` — open one remediation PR per affected workflow (max 1 per workflow per run)
- `noop` — emitted when no matching failures are found

## Behavior details

| Scenario | Outcome |
| --- | --- |
| No `Resource not accessible by integration` failures in last 24 h | `noop` — no PR opened |
| One workflow fails on one branch | One PR opened targeting that branch |
| Same workflow fails on multiple branches | One PR per branch to keep diffs reviewable |
| Multiple distinct workflows fail | One PR per workflow |

## External remediation instructions

The agent fetches remediation instructions at runtime from:

```
https://raw.githubusercontent.com/elastic/observability-cicd/main/github-actions/actionable/alerts/app/prompts/accessible-by-integration.txt
```

If the fetch fails the agent falls back to the general principle of adding the minimum required `permissions` block to the failing workflow jobs.

## Required permissions

The caller workflow must grant:

```yaml
permissions:
  actions: read
  contents: write
  pull-requests: write
```
