# Bug Exterminator

Fix bug-hunter issues by opening a focused PR.

## How it works

Searches for open issues labeled `bug-hunter` or titled `[bug-hunter]`. For each candidate, attempts to reproduce the bug locally — if reproduction succeeds and a minimal fix is safe to apply, it opens a PR. Most runs end with `noop`.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-exterminator/example.yml \
  -o .github/workflows/bug-exterminator.yml
````

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
