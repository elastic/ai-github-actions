# Stale Issues Remediator

Process stale-labeled issues: handle objections and close after a 30-day grace period.

## How it works

A scripted prep step fetches all open issues carrying the configured stale label, their recent comments, and label timeline events. The agent then processes each issue:

1. **Objections** — If someone commented "not stale", "still relevant", etc. after the label was added, the stale label is removed.
2. **30-day expiry** — Issues that have carried the label for 30+ days without objection are automatically closed with an explanatory comment.
3. **Grace period** — Issues still within the 30-day window are left alone.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues-remediator/example.yml \
  -o .github/workflows/stale-issues-remediator.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays (1h after investigator) |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `stale-label` | Label used to mark stale issues | No | `stale` |

## Safe Outputs

- `remove-labels` — remove the stale label when an objection is found
- `close-issue` — close issues that have been labeled stale for 30+ days

## Pairing

This workflow is the remediation companion to [Stale Issues Investigator](../stale-issues-investigator/). The investigator finds and labels stale candidates; the remediator handles objections and closes expired ones.
