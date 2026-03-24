# Internal Gemini CLI Web Search

Gemini-powered web research assistant — investigates issues and posts findings as comments or new issues.

## How it works

Activated by a comment on an issue (the example trigger uses `/research`). The workflow uses the Gemini engine to investigate local code and external sources via web fetch, then posts an evidence-backed response as a comment or creates a new issue when findings warrant separate tracking. It is strictly read-only and does not execute repository commands or implement changes.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/internal-gemini-cli-web-search/example.yml \
  -o .github/workflows/internal-gemini-cli-web-search.yml
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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `title-prefix` | Title prefix for created issues (e.g. `[research]`) | No | `[research]` |

## Required secret

- `GEMINI_API_KEY` — API key for Gemini engine authentication.

## Safe Outputs

- `add-comment` — reply to the issue with research findings
- `create-issue` — file a new issue when research reveals a distinct problem or action item
