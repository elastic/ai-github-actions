# Scheduled Audit

Generic base workflow for scheduled audits — investigate the repository and file an issue when something needs attention.

## How it works

The audit agent follows a standard 4-step process (gather context, analyze, quality gate, report) defined by the `scheduled-audit` fragment. You provide the **Report Assignment** via the `additional-instructions` input, which tells the agent what to investigate, what to look for, and how to report findings.

This is the base workflow. For domain-specific audits, see the specialized workflows:
- [Bug Hunter](../bug-hunter/) — find reproducible bugs
- [Text Auditor](../text-auditor/) — find text quality issues
- [Code Duplication Detector](../code-duplication-detector/) — find duplicate code
- [Breaking Change Detector](../breaking-change-detector/) — find breaking changes

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/scheduled-audit/example.yml \
  -o .github/workflows/scheduled-audit.yml
```

See [example.yml](example.yml) for the full workflow file. You **must** customize the `additional-instructions` input.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | What the audit agent should investigate (the Report Assignment) | **Yes** | — |
| `issue-title-prefix` | Title prefix for created issues, e.g. `[my-audit]` | **Yes** | — |
| `issue-label` | Label to apply to created issues | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `close-older-issues` | Whether to close older issues with the same title prefix when a new one is created | No | `true` |

## Safe Outputs

- `create-issue` — file an audit report (max 1, auto-closes older reports)
