# GitHub Agent Workflows

GitHub Agentic Workflows with safe-output guardrails. Engine and model are configurable per workflow, and updates are delivered via the `v0` tag.

## Install (caller-based, recommended)

Copy a workflow's `example.yml` from `gh-agent-workflows/` and customize inputs. No `gh-aw` CLI required.

````yaml
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
````

Each workflow directory contains an `example.yml` starter and a README for trigger details, inputs, and safe outputs.

## Available workflows

### Human-coordinated workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| [Issue Triage](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/issue-triage/README.md) | New issues | Investigate and provide implementation plans |
| [Issue Triage (with PR)](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/issue-triage-pr/README.md) | New issues | Triage plus automatic draft PR for straightforward fixes |
| [Mention in Issue](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/mention-in-issue/README.md) | `/ai` in issues | Answer questions, debug, create PRs |
| [Mention in PR](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/mention-in-pr/README.md) | `/ai` in PRs | Review, fix code, push changes |
| [PR CI Detective](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/pr-ci-detective/README.md) | Failed PR checks | Diagnose failures and recommend fixes |
| [PR CI Fixer](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/pr-ci-fixer/README.md) | Manual (workflow_dispatch) | Opt-in fixes for failed PR checks |
| [PR Checks Fix](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/pr-checks-fix/README.md) | Failed PR checks | Analyze and push fixes for failed PR checks |
| [PR Review](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/pr-review/README.md) | PR opened/updated | AI code review with inline comments |

### Continuous improvement / agent factory workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| [Agent Efficiency](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/agent-efficiency/README.md) | Weekday schedule | Analyze agent logs for inefficiencies |
| [Agent Suggestions](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/agent-suggestions/README.md) | Weekly schedule | Suggest new agent workflows based on repo and downstream needs |
| [Breaking Change Detect](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/breaking-change-detect/README.md) | Weekday schedule | Detect undocumented public breaking changes |
| [Bug Exterminator](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/bug-exterminator/README.md) | Weekday schedule | Fix bug-hunter issues and open a focused PR |
| [Bug Hunter](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/bug-hunter/README.md) | Weekday schedule | Find reproducible bugs and file reports |
| [Code Simplifier](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/code-simplifier/README.md) | Weekday schedule | Simplify overcomplicated code with high-confidence refactors |
| [Docs Drift](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/docs-drift/README.md) | Weekday schedule | Detect code changes needing doc updates |
| [Docs New Contributor Review](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/docs-new-contributor-review/README.md) | Weekly schedule | Review docs from a new contributor perspective |
| [Downstream Health](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/downstream-health/README.md) | Daily schedule | Monitor downstream repo quality |
| [Flaky Test Triage](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/flaky-test-triage/README.md) | Weekday schedule + failed CI runs | Identify repeated flaky failures and file root-cause-first triage reports |
| [Project Summary](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/project-summary/README.md) | Daily schedule | Summarize recent activity and priorities |
| [Release Update Check](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/release-update/README.md) | Weekly schedule | Open a PR updating pinned ai-github-actions workflow SHAs and suggest workflow changes |
| [Semantic Function Clustering](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/semantic-function-clustering/README.md) | Weekday schedule | Identify function clustering refactor opportunities |
| [Small Problem Fixer](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/small-problem-fixer/README.md) | Weekday schedule | Fix small, related issues and open a focused PR |
| [Stale Issues](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/stale-issues/README.md) | Weekday schedule | Find resolved issues that can be closed |
| [Test Improvement](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/test-improvement/README.md) | Weekly schedule | Add targeted tests and clean up redundant coverage |

## Secrets

These workflows require a Copilot PAT stored as `COPILOT_GITHUB_TOKEN`.

1. Create a Copilot PAT with the `copilot-requests` scope (the scope is only available for public repositories).
2. Store it as a repository secret:

````bash
gh aw secrets set COPILOT_GITHUB_TOKEN --value "(pat)"
````

UI path: Settings → Secrets and variables → Actions → New repository secret.

See the upstream [gh-aw auth docs](https://github.com/github/gh-aw/blob/main/docs/src/content/docs/reference/auth.mdx) for canonical steps.

## Agentic maintenance workflow required

Any workflow that uses safe-outputs with `expires` (create-issue, create-pull-request, create-discussion) requires the `agentics-maintenance` workflow so expired items are closed automatically. Install it once per repo:

````bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/.github/workflows/agentics-maintenance.yml \
  -o .github/workflows/agentics-maintenance.yml
````

## Standard inputs

All workflows accept these optional inputs via `workflow_call`:

| Input | Type | Description |
| --- | --- | --- |
| `additional-instructions` | string | Repo-specific instructions appended to the agent prompt |
| `setup-commands` | string | Shell commands to run before the agent starts (dependency install, build, etc.) |

### `setup-commands` examples

````yaml
# Python
setup-commands: |
  pip install -e ".[dev]"

# Node.js
setup-commands: |
  npm ci

# Go
setup-commands: |
  go mod download

# Multiple steps
setup-commands: |
  pip install -e ".[dev]"
  npm ci
  make build
````

## How it works

Each workflow has two layers:

1. **Workflow** (`gh-aw-*.md` -> `gh-aw-*.lock.yml`): The agent logic, compiled by `gh-aw`. Triggers only on `workflow_call` with standard inputs (`additional-instructions`, `setup-commands`) and a `COPILOT_GITHUB_TOKEN` secret.
2. **Trigger** (`<name>/example.yml`): A plain YAML file that defines the actual event triggers (schedule, PR events, slash commands, etc.) and calls the compiled `.lock.yml` via `uses:`. These serve as both examples for consumers and dogfood for this repo (copied to `.github/workflows/trigger-*.yml` by `scripts/dogfood.sh`).

Consumer repos copy a workflow's `example.yml`, change the `uses:` path if needed, and customize the `with:` inputs. Updates propagate automatically when this repo updates the `v0` tag on release.
