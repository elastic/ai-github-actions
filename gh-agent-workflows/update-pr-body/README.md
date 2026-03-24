# Update PR Body

Keep pull request bodies in sync with the code changes on every commit.

The updater also deduplicates any previously appended runtime footer text in the PR body before rewriting, so repeated runs do not stack duplicate footer blocks.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/update-pr-body/example.yml \
  -o .github/workflows/update-pr-body.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types | Condition |
| --- | --- | --- |
| `pull_request` | `opened`, `synchronize`, `reopened`, `ready_for_review` | PR is not a draft and does not have `skip-pr-body-update` label |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `edit-accuracy` | How aggressively to fix factual inaccuracies (`high`/`low`/`none`) | No | `low` |
| `edit-completeness` | How aggressively to add missing information about significant changes (`high`/`low`/`none`) | No | `low` |
| `edit-format` | How aggressively to improve markdown formatting and structure (`high`/`low`/`none`) | No | `none` |
| `edit-style` | How aggressively to improve writing style and clarity (`high`/`low`/`none`) | No | `none` |

### Edit Levels

Each edit dimension accepts one of three levels:

| Level | Meaning |
| --- | --- |
| `high` | Apply the agent's best judgment; proactively improve this dimension throughout the body |
| `low` | Make only conservative fixes for clear problems; do not restructure or rewrite |
| `none` | Do not touch this dimension at all; leave it exactly as the author wrote it |

## Safe Outputs

- `update-pull-request` — update the PR body when significant drift is detected
