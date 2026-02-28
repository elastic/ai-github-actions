# Breaking Change Detector

Detect undocumented breaking changes in public interfaces.

## How it works

Scans recent commits (1-day lookback, 3-day on Mondays) for public interface or behavioral changes. Cross-references each commit against its PR description, changelog, and documentation before concluding a change is undocumented.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/breaking-change-detector/example.yml \
  -o .github/workflows/breaking-change-detector.yml
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

## Labeling and assigning created issues

If you want detector-to-fixer handoff via labels, add these optional `workflow_dispatch` inputs to your local workflow copy and reference them from `additional-instructions`:

| Option | Description (with usage tips) | Suggested default |
| --- | --- | --- |
| `allowed-labels` | Comma-separated labels the agent is allowed to apply when it calls `create_issue`. Tip: include both a detector label and your handoff label (for example `ai:fix-ready`) so Issue Fixer can trigger from a labeled issue. Leave empty to skip labeling. | `breaking-change,ai:fix-ready` |
| `allowed-assignees` | Comma-separated GitHub usernames the agent is allowed to assign on created issues. Tip: keep this list small so assignment stays predictable. Leave empty to skip assigning. | `""` |

```yaml
on:
  workflow_dispatch:
    inputs:
      allowed-labels:
        description: "Comma-separated labels to allow on created issues"
        required: false
        default: "breaking-change,ai:fix-ready"
      allowed-assignees:
        description: "Comma-separated assignees to allow on created issues"
        required: false
        default: ""

jobs:
  run:
    with:
      additional-instructions: |
        When calling create_issue, apply these labels: `${{ inputs.allowed-labels || 'breaking-change,ai:fix-ready' }}`.
        If `${{ inputs.allowed-assignees || '' }}` is non-empty, assign the issue to those usernames.
```

## Safe Outputs

- `create-issue` — file a breaking change report (max 1, auto-closes older reports)
