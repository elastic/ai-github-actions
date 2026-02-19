# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## GitHub Agent Workflows (Recommended)

[GitHub Agentic Workflows](https://github.com/github/gh-aw) with safe-output guardrails. Engine and model are configurable per workflow.

Copy a workflow's `example.yml` from `gh-agent-workflows/` and customize inputs. No `gh-aw` CLI needed:

```yaml
# .github/workflows/trigger-pr-review.yml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-review.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

## Secrets

These workflows require a Copilot PAT stored as `COPILOT_GITHUB_TOKEN`.

1. Create a Copilot PAT with the `copilot-requests` scope (the scope is only available for public repositories).
2. Store it as a repository secret:

````bash
gh aw secrets set COPILOT_GITHUB_TOKEN --value "(pat)"
````

UI path: Settings → Secrets and variables → Actions → New repository secret.

See the upstream [gh-aw auth docs](https://github.com/github/gh-aw/blob/main/docs/src/content/docs/reference/auth.mdx) for canonical steps.

| Workflow | Trigger | Description |
| --- | --- | --- |
| PR Review | PR opened/updated | Automated code review with inline comments |
| Issue Triage | New issues | Investigate and provide implementation plans |
| Mention in Issue | `/ai` command | Answer questions, debug, create PRs |
| Mention in PR | `/ai` command | Review, fix code, push changes |
| PR Checks Fix | Failed PR checks | Analyze failures and optionally push fixes |
| Small Problem Fixer | Weekday schedule | Fix a small, related issue set and open a focused PR |
| Code Simplifier | Weekday schedule | Simplify overcomplicated code with high-confidence refactors |
| Test Improvement | Weekly schedule | Add targeted tests and clean up redundant coverage |
| Release Update Check | Weekly schedule | Open a PR updating pinned ai-github-actions workflow SHAs and suggest workflow changes |
| Bug Hunter | Weekday schedule | Find a reproducible, user-impacting bug and file an issue |
| Bug Exterminator | Weekday schedule | Fix bug-hunter issues and open a focused PR |
| Docs Drift | Weekday schedule | Detect code changes needing doc updates |
| Docs New Contributor Review | Weekly schedule | Review docs from a new contributor perspective |
| Project Summary | Daily schedule | Summarize recent activity and priorities |
| Breaking Change Detect | Weekday schedule | Detect undocumented public breaking changes |
| Semantic Function Clustering | Weekday schedule | Identify semantic function clustering refactor opportunities |

See **[gh-agent-workflows/](gh-agent-workflows/)** for install commands, customization, and updating.

## Choosing an Approach

| Feature | GitHub Agent Workflows | Claude Composite Actions |
| --- | --- | --- |
| **Engine** | Copilot (default) or Claude | Claude only |
| **Install** | Copy trigger YAML (recommended) or `gh aw add` + `gh aw compile` | Copy `example.yml` to `.github/workflows/` |
| **Guardrails** | Safe-outputs framework (structured API outputs) | Read-only/RWX/RWXP variants via permissions |
| **Customization** | `additional-instructions` input, `setup-commands` input, or full shim edit | Edit YAML directly, adjust composite action inputs |

GitHub Agent Workflows are recommended for new deployments — they're more flexible and have better guardrails. Claude Composite Actions are still supported for legacy deployments.

## Composite Actions (Claude Code)

Traditional GitHub Actions wrapping [Claude Code](https://github.com/anthropics/claude-code-action). Consumed via `uses:` in standard YAML workflows.

```yaml
uses: elastic/ai-github-actions/claude-workflows/pr-review/rwx@v0
```

Includes review agents, assistant agents, build failure analyzers, and report generators — each with configurable permission levels (RO, RWX, RWXP).

See **[claude-workflows/](claude-workflows/)** for the full catalog and configuration.

> **Note:** `claude-workflows/` was renamed from `workflows/`. A symlink ensures backwards compatibility.

## License

MIT
