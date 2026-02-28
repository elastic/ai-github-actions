# Resource Not Accessible By Integration Detector

Daily detector that scans for `Resource not accessible by integration` errors across long-term branches and opens one combined tracking issue.

## How it works

Runs once every 24 hours (or manually). A prescan script runs before the agent prompt: it queries failed workflow runs from the configured look-back window on the default branch and any configured long-term (release) branches, downloads logs, searches for the exact error text `Resource not accessible by integration`, and writes matches to `/tmp/gh-aw/agent/resource-not-accessible-findings.tsv`. The agent then analyzes only those prescanned workflows and opens **one combined issue** with the results. If no matching failures are found, the run ends with `noop`.

The generated issue:
- includes grouped workflow/run links plus verbatim evidence lines;
- provides a root-cause assessment and remediation guidance;
- avoids reposting when an equivalent open issue already exists.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-actions-resource-not-accessible-detector/example.yml \
  -o .github/workflows/estc-actions-resource-not-accessible-detector.yml
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
| `look-back-days` | Number of days to look back when scanning failed workflow runs | No | `1` |
| `issue-title-prefix` | Title prefix used for the combined issue and dedup checks | No | `[resource-not-accessible-by-integration]` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Labeling and assigning created issues

If you want detector-to-fixer handoff via labels, add these optional `workflow_dispatch` inputs to your local workflow copy and reference them from `additional-instructions`:

| Option | Description (with usage tips) | Suggested default |
| --- | --- | --- |
| `allowed-labels` | Comma-separated labels the agent is allowed to apply when it calls `create_issue`. Tip: include both a detector label and your handoff label (for example `ai:fix-ready`) so Issue Fixer can trigger from a labeled issue. Leave empty to skip labeling. | `resource-not-accessible-by-integration,ai:fix-ready` |
| `allowed-assignees` | Comma-separated GitHub usernames the agent is allowed to assign on created issues. Tip: keep this list small so assignment stays predictable. Leave empty to skip assigning. | `""` |

```yaml
on:
  workflow_dispatch:
    inputs:
      allowed-labels:
        description: "Comma-separated labels to allow on created issues"
        required: false
        default: "resource-not-accessible-by-integration,ai:fix-ready"
      allowed-assignees:
        description: "Comma-separated assignees to allow on created issues"
        required: false
        default: ""

jobs:
  run:
    with:
      additional-instructions: |
        When calling create_issue, apply these labels: `${{ inputs.allowed-labels || 'resource-not-accessible-by-integration,ai:fix-ready' }}`.
        If `${{ inputs.allowed-assignees || '' }}` is non-empty, assign the issue to those usernames.
```

## Safe Outputs

- `create-issue` — open one combined issue with analysis for all affected workflows
- `noop` — emitted when no matching failures are found

## Behavior details

| Scenario | Outcome |
| --- | --- |
| No `Resource not accessible by integration` failures in look-back window | `noop` — no issue opened |
| One workflow fails on one branch | Combined issue includes one workflow entry |
| Same workflow fails on multiple branches | Combined issue includes all affected branches/runs under one workflow |
| Multiple distinct workflows fail | Combined issue includes all workflows in one report |
| Findings already tracked by an open prefixed issue | `noop` — avoid duplicate repost |

## Remediation guidance

The agent includes a built-in permission reference table mapping failed GitHub API operations to required `GITHUB_TOKEN` scopes. For each affected workflow it reads the source file, identifies the failing operation from log evidence, and recommends the minimum `permissions:` block to add.

## Similar behavior with base Scheduled Audit

If you prefer a generic setup, you can get similar behavior with [Scheduled Audit](../scheduled-audit/) by:
- setting an issue title prefix dedicated to this error class,
- adding instructions to prescan recent failed runs/logs for `Resource not accessible by integration`,
- emitting one combined issue and `noop` when no findings or already tracked findings exist.

## Required permissions

The caller workflow must grant:

```yaml
permissions:
  actions: read
  contents: read
  issues: write
```
