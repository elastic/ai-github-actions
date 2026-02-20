# Small Problem Fixer

Find small, related issues and open a focused PR.

## How it works

Searches open issues for small, actionable candidates — first by labels (`good first issue`, `small`, `quick fix`, `easy`) then by low comment count (≤2). Only considers issues authored by trusted members (`OWNER`, `MEMBER`, or `COLLABORATOR`). Picks one issue (or up to three tightly related issues with a shared root cause), implements the smallest safe fix, verifies it with tests, and opens a PR. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/small-problem-fixer/example.yml \
  -o .github/workflows/small-problem-fixer.yml
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

## Safe Outputs

- `create-pull-request` — open a PR with the fix
