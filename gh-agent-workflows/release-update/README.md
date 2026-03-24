# Release Update Check

Check for new ai-github-actions releases and open a PR updating pinned workflow SHAs, with suggestions based on release notes.

## How it works

Checks the elastic/ai-github-actions releases page for versions newer than the ones pinned in the repo's workflow files. When a new release is found, opens a PR that updates all pinned SHA references and summarizes the relevant release notes.

## Quick Install

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/release-update/example.yml \
  -o .github/workflows/release-update.yml
````

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-pull-request` — open a PR with workflow reference updates
