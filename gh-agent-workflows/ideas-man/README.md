# Ideas Man

Propose well-researched new feature ideas as GitHub issues.

## How it works

Reviews the codebase, recent activity, and existing issues to propose a single new feature idea that is customer-aligned, grounded in the existing code, and tractable. Each idea includes a rough implementation sketch and a "why it won't be that hard" rationale. Only files an issue when a genuinely useful, non-duplicate idea is found — most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/ideas-man/example.yml \
  -o .github/workflows/ideas-man.yml
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

- `create-issue` — file a feature idea (max 1, auto-closes older reports)
