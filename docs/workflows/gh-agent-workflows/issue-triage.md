# Issue Triage

Investigate new issues and provide actionable triage analysis.

When a new issue is opened, reads the issue and related code, reproduces or validates the report where possible, and posts a comment with a root cause analysis and actionable next steps.

## Quick install

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-triage/example.yml \
  -o .github/workflows/trigger-issue-triage.yml
```

---

## Trigger

| Event | Types |
| --- | --- |
| `issues` | `opened` |

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt. | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `COPILOT_GITHUB_TOKEN` | GitHub Copilot PAT for AI engine authentication | Yes |
| `GH_AW_GITHUB_TOKEN` | Ephemeral token (e.g. a GitHub App token) used for issue labeling safe outputs. When provided, labels applied by this workflow will trigger downstream label-based workflows. When omitted, the built-in `GITHUB_TOKEN` is used, which does not re-trigger other workflows. | No |

## Safe outputs

- `add-comment` — post a triage analysis comment on the issue

## Example workflow

```yaml
name: Issue Triage
on:
  issues:
    types: [opened]

permissions:
  actions: read
  contents: read
  discussions: write
  issues: write
  pull-requests: write

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-issue-triage.lock.yml@v0
    # with:
      # setup-commands: |
      #   echo "Optional setup runs before triage begins"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
      # Optional: pass an ephemeral token (e.g. a GitHub App token) so that issue labels
      # applied by this workflow can trigger downstream label-based workflows.
      # When omitted, the built-in GITHUB_TOKEN is used for labeling, which does
      # not re-trigger other workflows.
      # GH_AW_GITHUB_TOKEN: ${{ secrets.GH_AW_GITHUB_TOKEN }}
```
