# Text Beautifier

Fix text-auditor issues by opening a focused PR with text improvements.

## How it works

Picks up open issues filed by the Text Auditor (labeled `text-auditor` or with `[text-auditor]` in the title), applies the suggested text fixes, and opens a PR. Only acts on concrete, unambiguous fixes — skips anything requiring design decisions. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-beautifier/example.yml \
  -o .github/workflows/text-beautifier.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-pull-request` — open a PR with text fixes (max 1)

## Pairing

This workflow is the read-write companion to [Text Auditor](../text-auditor/). The auditor finds issues; the beautifier fixes them.
