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
| Issue Triage | New issues | Investigate and provide implementation plans |
| Issue Triage (with PR) | New issues | Triage plus automatic draft PR for straightforward fixes |
| Mention in Issue | `/ai` in issues | Answer questions, debug, create PRs |
| Mention in PR | `/ai` in PRs | Review, fix code, push changes |
| PR CI Detective | Failed PR checks | Diagnose failures and recommend fixes |
| PR CI Fixer | Manual (workflow_dispatch) | Opt-in fixes for failed PR checks |
| PR Review | PR opened/updated | AI code review with inline comments |

### Continuous improvement / agent factory workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| Agent Efficiency | Weekday schedule | Analyze agent logs for inefficiencies |
| Agent Suggestions | Weekly schedule | Suggest new agent workflows based on repo and downstream needs |
| Breaking Change Detect | Weekday schedule | Detect undocumented public breaking changes |
| Bug Exterminator | Weekday schedule | Fix bug-hunter issues and open a focused PR |
| Bug Hunter | Weekday schedule | Find reproducible bugs and file reports |
| Code Simplifier | Weekday schedule | Simplify overcomplicated code with high-confidence refactors |
| Docs Drift | Weekday schedule | Detect code changes needing doc updates |
| Docs New Contributor Review | Weekly schedule | Review docs from a new contributor perspective |
| Downstream Health | Daily schedule | Monitor downstream repo quality |
| Flaky Test Triage | Weekday schedule + failed CI runs | Identify repeated flaky failures and file root-cause-first triage reports |
| Project Summary | Daily schedule | Summarize recent activity and priorities |
| Release Update Check | Weekly schedule | Open a PR updating pinned ai-github-actions workflow SHAs and suggest workflow changes |
| Semantic Function Clustering | Weekday schedule | Identify function clustering refactor opportunities |
| Small Problem Fixer | Weekday schedule | Fix small, related issues and open a focused PR |
| Stale Issues | Weekday schedule | Find resolved issues that can be closed |
| Test Improvement | Weekly schedule | Add targeted tests and clean up redundant coverage |

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
