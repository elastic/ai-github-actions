# Issue Fixer — workflows

Investigate new issues and provide actionable triage analysis. For straightforward fixes — including verified remediations under `.github/workflows/` — implement and open a draft PR.

## How it differs from Issue Fixer

| | [Issue Fixer](../issue-fixer/README.md) | Issue Fixer — workflows |
| --- | --- | --- |
| Workflow / `.github/` PRs | Prompt guardrails discourage; safe-outputs block top-level dot folders | Allowed when verified; `.github/` opted out of dot-folder protection |
| Typical use | General issue remediations | Security / CI remediations that edit workflow YAML |
| Token | Prefer `github-token-policy` for CI re-trigger | Prefer `github-token-policy` (required in practice for workflow-file pushes) |

Keep using `gh-aw-issue-fixer` for generic fixers. Use this lock when callers intentionally need draft PRs that touch `.github/`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-fixer-workflows/example.yml \
  -o .github/workflows/issue-fixer-workflows.yml
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
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated); also GH-AW trusted-users under min-integrity approved | No | `github-actions[bot]` |
| `report-failure-as-issue` | When `true`, agent failures are reported as a GitHub issue | No | `true` |
| `github-token-policy` | **Elastic-specific.** Backstage TokenPolicy id for `elastic/oblt-actions/github/create-token`. When set, mint an OIDC ephemeral GitHub token in each token-consuming job so pull requests and comments re-trigger downstream workflows. Requires Elastic TokenPolicy / ephemeral-token infrastructure; leave empty outside Elastic. The caller job must grant `id-token: write`. Prefer setting this for workflow-file remediations. | No | `""` |

## Secrets

| Secret | Description | Required |
| --- | --- | --- |
| `GH_AW_GITHUB_TOKEN` | Optional override token for GitHub API writes. Prefer `github-token-policy` with OIDC when available. | No |
| `EXTRA_COMMIT_GITHUB_TOKEN` | Optional token used to push an extra empty commit so PRs created with `GITHUB_TOKEN` still trigger CI. Not needed when `github-token-policy` is set. | No |

## Safe Outputs

- `add-comment` — post triage analysis on the issue
- `create-pull-request` — open a draft PR when a verified fix is implemented (including `.github/` paths)
