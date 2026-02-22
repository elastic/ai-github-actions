# Mention in Issue (no sandbox)

AI assistant for issues — answer questions, debug, and create PRs on demand. The agent sandbox is disabled, allowing direct Docker access.

## How it works

Activated by a comment on an issue (the example trigger uses `/ai`, but the prefix is configurable). Reads the issue context and codebase, then answers questions, debugs problems, suggests solutions, or opens a PR with a proposed fix.

This variant runs **without the agent sandbox** (`sandbox.agent: false`), which means the agent has direct access to the Docker daemon. Use this when your `setup-commands` need to build or run Docker containers.

> ⚠️ **Security note**: Disabling the agent sandbox removes the network firewall and filesystem isolation that the sandboxed variant provides. Use only when Docker access is required.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-issue-no-sandbox/example.yml \
  -o .github/workflows/mention-in-issue-no-sandbox.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment on an issue (not a PR); the example trigger filters on `/ai` prefix |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — reply to the issue
- `create-pull-request` — open a PR with code changes
- `create-issue` — file a new issue
