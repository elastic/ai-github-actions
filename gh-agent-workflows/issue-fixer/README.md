# Issue Fixer

Investigate new issues and provide actionable triage analysis. For straightforward fixes, implement and open a draft PR.

## How it works

Same as Issue Triage, but also implements the fix and opens a draft PR when the fix is straightforward and safe to land quickly.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-fixer/example.yml \
  -o .github/workflows/issue-fixer.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `issues` | `opened` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `report-failure-as-issue` | When `true`, agent failures are reported as a GitHub issue | No | `true` |
| `mint-ephemeral-token` | When `true`, mint an OIDC ephemeral GitHub token in each token-consuming job (`elastic/oblt-actions/github/create-token`). Pull requests and comments then re-trigger downstream workflows. The caller job must grant `id-token: write`. | No | `false` |
| `token-policy` | Backstage TokenPolicy id for `create-token`. Empty uses Vault auto policy from the triggering `workflow_ref`. Used only when `mint-ephemeral-token` is `true`. | No | `""` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `GH_AW_GITHUB_TOKEN` | Optional override token for GitHub API writes. Prefer `mint-ephemeral-token` with OIDC when available. | No |
| `EXTRA_COMMIT_GITHUB_TOKEN` | Optional token used to push an extra empty commit so PRs created with `GITHUB_TOKEN` still trigger CI. Not needed when `mint-ephemeral-token` is `true`. | No |

## Safe Outputs

- `add-comment` — post triage analysis on the issue
- `create-pull-request` — open a draft PR when a verified fix is implemented
