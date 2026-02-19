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
| PR Review | PR opened/updated | AI code review with inline comments |
| Issue Triage | New issues | Investigate and provide implementation plans |
| Mention in Issue | `/ai` in issues | Answer questions, debug, create PRs |
| Mention in PR | `/ai` in PRs | Review, fix code, push changes |
| PR CI Detective | Failed PR checks | Diagnose failures and recommend fixes |
| PR CI Fixer | Manual (workflow_dispatch) | Opt-in fixes for failed PR checks |

### Continuous improvement / agent factory workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| Small Problem Fixer | Weekday schedule | Fix small, related issues and open a focused PR |
| Code Simplifier | Weekday schedule | Simplify overcomplicated code with high-confidence refactors |
| Test Improvement | Weekly schedule | Add targeted tests and clean up redundant coverage |
| Release Update Check | Weekly schedule | Open a PR updating pinned ai-github-actions workflow SHAs and suggest workflow changes |
| Agent Suggestions | Weekly schedule | Suggest new agent workflows based on repo and downstream needs |
| Bug Hunter | Weekday schedule | Find reproducible bugs and file reports |
| Bug Exterminator | Weekday schedule | Fix bug-hunter issues and open a focused PR |
| Flaky Test Triage | Weekday schedule + failed CI runs | Identify repeated flaky failures and file root-cause-first triage reports |
| Docs Drift | Weekday schedule | Detect code changes needing doc updates |
| Docs New Contributor Review | Weekly schedule | Review docs from a new contributor perspective |
| Project Summary | Daily schedule | Summarize recent activity and priorities |
| Downstream Health | Daily schedule | Monitor downstream repo quality |
| Breaking Change Detect | Weekday schedule | Detect undocumented public breaking changes |
| Semantic Function Clustering | Weekday schedule | Identify function clustering refactor opportunities |
| Stale Issues | Weekday schedule | Find resolved issues that can be closed |
| Agent Efficiency | Weekday schedule | Analyze agent logs for inefficiencies |

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

## Classic installation (with gh-aw)

For repos that want local compilation and full customization (engine, permissions, safe-outputs), the `gh aw add` path is still supported.

**Prerequisites:** [GitHub CLI](https://cli.github.com/), [gh-aw extension](https://github.com/github/gh-aw) (`gh extension install github/gh-aw`), Go 1.25+.

````bash
# Install a workflow (classic install pulls the workflow .md from this repo)
gh aw add elastic/ai-github-actions/gh-agent-workflows/pr-review.md

# Compile to generate the lock file
gh aw compile

# Commit both files and push
git add .github/workflows/gh-aw-pr-review.md .github/workflows/gh-aw-pr-review.lock.yml
git commit -m "Add PR review workflow"
git push
````

Note: with classic installation, you own the full `.md` shim and compile locally. You'll still need a trigger workflow (plain YAML) to define event triggers separately, since the compiled `.lock.yml` only accepts `workflow_call`.

## How it works

Each workflow has two layers:

1. **Workflow** (`gh-aw-*.md` -> `gh-aw-*.lock.yml`): The agent logic, compiled by `gh-aw`. Triggers only on `workflow_call` with standard inputs (`additional-instructions`, `setup-commands`) and a `COPILOT_GITHUB_TOKEN` secret.
2. **Trigger** (`<name>/example.yml`): A plain YAML file that defines the actual event triggers (schedule, PR events, slash commands, etc.) and calls the compiled `.lock.yml` via `uses:`. These serve as both examples for consumers and dogfood for this repo (copied to `.github/workflows/trigger-*.yml` by `scripts/dogfood.sh`).

Consumer repos copy a workflow's `example.yml`, change the `uses:` path if needed, and customize the `with:` inputs. Updates propagate automatically when this repo updates the `v0` tag on release.

## Customization (classic installation)

### Change the AI engine or model

The default is Copilot with gpt-5.2-codex. Override in the workflow's frontmatter:

````yaml
engine:
  id: copilot
  model: claude-sonnet-4-20250514
````

### Override permissions or timeouts

````yaml
permissions:
  contents: read
  issues: read
  pull-requests: read
timeout-minutes: 30
````

### Add tools or MCP servers

Tools and network allows from imports merge additively — add your own in the workflow `.md`:

````yaml
tools:
  bash: ["npm", "npx", "node"]
mcp-servers:
  my-custom-server:
    url: "https://my-server.example.com/mcp"
    allowed: ["my_tool"]
network:
  allowed:
    - "my-server.example.com"
````

Each workflow already includes `github` (repos, issues, pull_requests, search), `bash`, and `web-fetch` tools with `defaults` and `github` network access. Anything you add in the shim merges on top.

### Override safe outputs

Workflow-level safe-outputs override imported defaults:

````yaml
safe-outputs:
  add-comment:
    max: 5
````

### Add setup steps

Install tools the agent needs (e.g., language runtimes, build tools):

````yaml
steps:
  - uses: actions/setup-go@v5
    with:
      go-version: "1.23"
````

### Customize prompt content

Workflows contain their prompts directly in the `.md` body. Add instructions inline or via the workflow's frontmatter:

````yaml
# .github/workflows/gh-aw-docs-drift.md
---
# frontmatter ...
---
````

````markdown
Detect documentation drift in recent commits. Focus on API docs and README updates.
Add any repo-specific instructions here.
````

The `${{ inputs.additional-instructions }}` append mechanism also lets callers inject repo-specific guidance without editing the workflow file.

## Updating

````bash
# Update a specific workflow's shim to latest
gh aw update pr-review

# Update all workflows
gh aw update
````

`gh aw update` does a 3-way merge preserving your customizations. Shared imports (prompts, tools, formatting) update automatically on recompile — you only need `gh aw update` when the shim itself changes.
