# Scheduled Fix

Generic base workflow for scheduled fixers — pick up an open issue and create a focused PR that addresses it.

## How it works

The fix agent follows a standard 5-step process (gather candidates, select target, implement, quality gate, create PR) defined by the `scheduled-fix` fragment. You provide the **Fix Assignment** via the `additional-instructions` input, which tells the agent how to find issues, what kind of changes to make, and any domain-specific constraints.

This is the base workflow. For domain-specific fixers, see the specialized workflows:
- [Bug Exterminator](../bug-exterminator/) — fix bug-hunter issues
- [Text Beautifier](../text-beautifier/) — fix text-auditor issues
- [Code Duplication Fixer](../code-duplication-fixer/) — fix code-duplication-detector issues

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/scheduled-fix/example.yml \
  -o .github/workflows/scheduled-fix.yml
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
| `additional-instructions` | Domain-specific fix instructions (the Fix Assignment) | **Yes** | — |
| `title-prefix` | Title prefix to search for in open issues, e.g. `[my-audit]` | **Yes** | — |
| `issue-label` | Label to search for in open issues | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `draft-prs` | Create PRs as draft (true/false) | No | `true` |

## Safe Outputs

- `create-pull-request` — open a PR with the fix (max 1)

## Pairing

Pair this with a [Scheduled Audit](../scheduled-audit/) workflow. The audit detects issues; the fix resolves them.
