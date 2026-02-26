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
| `look-back-days` | Number of days to look back when scanning failed workflow runs | No | `1` |
| `issue-title-prefix` | Title prefix used for the combined issue and dedup checks | No | `[resource-not-accessible-by-integration]` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

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

## External remediation instructions

The agent fetches remediation instructions at runtime from:

```
https://raw.githubusercontent.com/elastic/observability-cicd/main/github-actions/actionable/alerts/app/prompts/accessible-by-integration.txt
```

If the fetch fails the agent falls back to the general principle of adding the minimum required `permissions` block to the failing workflow jobs.

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
