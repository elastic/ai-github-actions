# Deep Research

Deep research assistant for issue comments with web search/fetch and optional PR creation.

## How it works

Activated by a comment on an issue (the example trigger uses `/research`). The workflow investigates local code and external sources, then posts an evidence-backed response and can open a PR when implementation is requested.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/deep-research/example.yml \
  -o .github/workflows/deep-research.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on an issue (not a PR); the example trigger filters on `/research` prefix |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Required secret

- `ANTHROPIC_API_KEY` — API key for Claude engine authentication.

## Safe Outputs

- `add-comment` — reply to the issue with research findings
- `create-pull-request` — open a PR with code changes
- `create-issue` — file a follow-up issue when splitting work helps
