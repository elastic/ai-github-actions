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
| `additional-instructions` | Repo-specific instructions appended to the agent prompt. Use this to define label semantics for `classification-labels`. | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | `github-actions[bot]` |
| `classification-labels` | Comma-separated list of labels the agent may apply (e.g. `bug,needs-triage,enhancement`). If empty, no labels are applied. Define label semantics in `additional-instructions`. | `""` |
| `report-failure-as-issue` | When `true`, agent failures are reported as a GitHub issue | `true` |
| `github-token-policy` | Backstage TokenPolicy id for `create-token`. When set, mint an OIDC ephemeral GitHub token in each token-consuming job so labels re-trigger downstream workflows. The caller job must grant `id-token: write`. | `""` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `GH_AW_GITHUB_TOKEN` | Optional override token for GitHub API writes. Prefer `github-token-policy` with OIDC when available. When neither is set, `GITHUB_TOKEN` is used and label writes do not re-trigger other workflows. | No |

## Safe outputs

- `add-comment` — post a triage analysis comment on the issue
- `add-labels` — apply labels from the configured `classification-labels` allowlist (max 3); semantics defined via `additional-instructions`

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
  id-token: write

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-issue-triage.lock.yml@v0
    # with:
      # Configure which labels the agent may apply and define their semantics in additional-instructions.
      # classification-labels: "bug,needs-triage,enhancement"
      # additional-instructions: |
      #   - `bug`: Apply when the issue describes a clear defect or unexpected behavior.
      #   - `needs-triage`: Apply when more information is needed before the issue can be acted on.
      #   - `enhancement`: Apply when the issue describes a new feature or improvement request.
      # Elastic OIDC: github-token-policy: "<shared-token-policy-id>"
```
