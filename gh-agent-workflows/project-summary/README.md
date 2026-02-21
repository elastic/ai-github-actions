# Project Summary

Create a periodic project summary issue covering recent activity, priorities, and next steps.

## How it works

Finds the last project summary issue to determine the reporting window, then collects commits, opened and merged PRs, and updated issues. Highlights items needing attention — stale reviews, blocking issues, decisions needed — in a concise periodic report.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/project-summary/example.yml \
  -o .github/workflows/project-summary.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Daily |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Storyteller / chronicler example

Use `additional-instructions` to switch from a neutral status report to a narrative "project chronicler" style without creating a separate workflow:

````yaml
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-project-summary.lock.yml@v0
    with:
      additional-instructions: |
        Write the summary as a project chronicler.
        Keep all factual details accurate and link-backed, but present sections in a story-like narrative voice.
        End with "Chronicle Next Steps" as a checklist of concrete actions.
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
````

## Safe Outputs

- `create-issue` — file a project summary report (max 1, auto-closes older reports)
