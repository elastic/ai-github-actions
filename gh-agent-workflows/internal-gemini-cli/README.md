# Internal Gemini CLI

Gemini-powered code investigation assistant — investigates issues using bash and posts findings as comments or new issues.

## How it works

Activated by a comment on an issue (the example trigger uses `/gemini`). The workflow uses the Gemini engine with bash access to investigate code, run tests, check builds, and inspect the repository, then posts an evidence-backed response as a comment or creates a new issue when findings warrant separate tracking.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/internal-gemini-cli/example.yml \
  -o .github/workflows/internal-gemini-cli.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on an issue (not a PR); the example trigger filters on `/gemini` prefix |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `title-prefix` | Title prefix for created issues (e.g. `[gemini-cli]`) | No | `[gemini-cli]` |

## Required secret

- `GEMINI_API_KEY` — API key for Gemini engine authentication.

## Safe Outputs

- `add-comment` — reply to the issue with investigation findings
- `create-issue` — file a new issue when investigation reveals a distinct problem or action item
