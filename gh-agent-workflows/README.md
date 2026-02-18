# GitHub Agent Workflows

[GitHub Agentic Workflows](https://github.com/github/gh-aw) for Elastic repositories. All write operations go through [safe-outputs](https://github.github.io/gh-aw/reference/safe-outputs/) for security.

## Available Workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| PR Review | PR opened/updated | AI code review with inline comments |
| Issue Triage | New issues | Investigate and provide implementation plans |
| Mention in Issue | `/ai` in issues | Answer questions, debug, create PRs |
| Mention in PR | `/ai` in PRs | Review, fix code, push changes |
| PR Checks Fix | Failed PR checks | Analyze failures and optionally push fixes |
| Small Problem Fixer | Weekday schedule | Fix small, related issues and open a focused PR |
| Code Simplifier | Weekday schedule | Simplify overcomplicated code with high-confidence refactors |
| Test Improvement | Weekly schedule | Add targeted tests and clean up redundant coverage |
| Bug Hunter | Weekday schedule | Find reproducible bugs and file reports |
| Docs Drift | Weekday schedule | Detect code changes needing doc updates |
| Downstream Health | Daily schedule | Monitor downstream repo quality |
| Breaking Change Detect | Weekday schedule | Detect undocumented public breaking changes |
| Semantic Function Clustering | Weekday schedule | Identify function clustering refactor opportunities |

## Quick Start (Caller-Based, Recommended)

Create a plain YAML workflow in your repo that calls the pre-compiled workflow from this repo. No `gh-aw` CLI needed.

```yaml
# .github/workflows/pr-review.yml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-review.lock.yml@v0
    with:
      setup-commands: |
        pip install -e ".[dev]"
      additional-instructions: |
        Focus on Python best practices and type safety.
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

Commit and push. The workflow triggers on your repo's events and delegates to the centrally-compiled agent workflow. Updates propagate automatically when this repo recompiles -- no action needed in your repo.

### Standard Inputs

All workflows accept these optional inputs via `workflow_call`:

| Input | Type | Description |
| --- | --- | --- |
| `additional-instructions` | string | Repo-specific instructions appended to the agent prompt |
| `setup-commands` | string | Shell commands to run before the agent starts (dependency install, build, etc.) |

### `setup-commands` Examples

```yaml
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
```

### Consumer Caller Templates

**Scheduled workflows** (test-improvement, code-simplifier, small-problem-fixer, bug-hunter, stale-issues, docs-drift, downstream-health, breaking-change-detect, semantic-function-clustering, agent-efficiency):

```yaml
name: <Workflow Name>
on:
  schedule:
    - cron: "<your schedule>"
  workflow_dispatch:
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-<name>.lock.yml@v0
    with:
      setup-commands: |
        <your setup commands>
      additional-instructions: |
        <your repo-specific instructions>
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

**Slash command workflows** (mention-in-issue, mention-in-pr):

```yaml
name: <Workflow Name>
on:
  issue_comment:
    types: [created]
jobs:
  run:
    if: startsWith(github.event.comment.body, '/ai')
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-<name>.lock.yml@v0
    with:
      additional-instructions: |
        <your repo-specific instructions>
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

**PR review** (pr-review):

```yaml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review, labeled, unlabeled]
jobs:
  run:
    if: >-
      github.event.pull_request.draft == false &&
      !contains(github.event.pull_request.labels.*.name, 'skip-auto-pr-review')
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-review.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

**Issue triage** (issue-triage):

```yaml
name: Issue Triage
on:
  issues:
    types: [opened]
jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-issue-triage.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

**PR checks fix** (pr-checks-fix):

```yaml
name: PR Checks Fix
on:
  workflow_run:
    workflows: ["CI"]  # replace with your CI workflow name(s)
    types: [completed]
jobs:
  run:
    if: >-
      github.event.workflow_run.conclusion == 'failure' &&
      toJSON(github.event.workflow_run.pull_requests) != '[]'
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-pr-checks-fix.lock.yml@v0
    with:
      setup-commands: |
        <your setup commands>
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

## Classic Installation (With gh-aw)

For repos that want local compilation and full customization (engine, permissions, safe-outputs), the `gh aw add` path is still supported.

**Prerequisites:** [GitHub CLI](https://cli.github.com/), [gh-aw extension](https://github.com/github/gh-aw) (`gh extension install github/gh-aw`), Go 1.25+.

```bash
# Install a workflow (classic install pulls the workflow .md from this repo)
gh aw add elastic/ai-github-actions/gh-agent-workflows/pr-review.md

# Compile to generate the lock file
gh aw compile

# Commit both files and push
git add .github/workflows/gh-aw-pr-review.md .github/workflows/gh-aw-pr-review.lock.yml
git commit -m "Add PR review workflow"
git push
```

Note: with classic installation, you own the full `.md` shim and compile locally. You'll still need a trigger workflow (plain YAML) to define event triggers separately, since the compiled `.lock.yml` only accepts `workflow_call`.

## How It Works

Each workflow has two layers:

1. **Workflow** (`gh-aw-*.md` -> `gh-aw-*.lock.yml`): The agent logic, compiled by `gh-aw`. Triggers only on `workflow_call` with standard inputs (`additional-instructions`, `setup-commands`) and a `COPILOT_GITHUB_TOKEN` secret.
2. **Trigger** (`trigger-*.yml` in `.github/workflows/`): A plain YAML file that defines the actual event triggers (schedule, PR events, slash commands, etc.) and calls the compiled `.lock.yml` via `uses:`. These serve as both examples for consumers and dogfood for this repo.

Consumer repos copy a trigger file from `.github/workflows/`, change the `uses:` path from `./.github/workflows/gh-aw-...` to `elastic/ai-github-actions/.github/workflows/gh-aw-...@main`, and customize the `with:` inputs. No `gh-aw` CLI needed. Updates propagate automatically when this repo recompiles and pushes to `main`.

## Customization (Classic Installation)

For classic `gh aw add` consumers: edit the workflow `.md` file in `.github/workflows/` and recompile with `gh aw compile`.

### Change the AI engine or model

The default is Copilot with gpt-5.2-codex. Override in the workflow's frontmatter:

```yaml
engine:
  id: copilot
  model: claude-sonnet-4-20250514
```

### Override permissions or timeouts

```yaml
permissions:
  contents: read
  issues: read
  pull-requests: read
timeout-minutes: 30
```

### Add tools or MCP servers

Tools and network allows from imports merge additively — add your own in the workflow `.md`:

```yaml
tools:
  bash: ["npm", "npx", "node"]
mcp-servers:
  my-custom-server:
    url: "https://my-server.example.com/mcp"
    allowed: ["my_tool"]
network:
  allowed:
    - "my-server.example.com"
```

Each workflow already includes `github` (repos, issues, pull_requests, search), `bash`, and `web-fetch` tools with `defaults` and `github` network access. Anything you add in the shim merges on top.

### Override safe outputs

Workflow-level safe-outputs override imported defaults:

```yaml
safe-outputs:
  add-comment:
    max: 5
```

### Add setup steps

Install tools the agent needs (e.g., language runtimes, build tools):

```yaml
steps:
  - uses: actions/setup-go@v5
    with:
      go-version: '1.23'
```

### Customize prompt content

Workflows contain their prompts directly in the `.md` body. Add instructions inline or via the workflow's frontmatter:

```yaml
# .github/workflows/gh-aw-docs-drift.md
---
# frontmatter ...
---
```

```markdown
Detect documentation drift in recent commits. Focus on API docs and README updates.
Add any repo-specific instructions here.
```

The `${{ inputs.additional-instructions }}` append mechanism also lets callers inject repo-specific guidance without editing the workflow file.

## Updating

```bash
# Update a specific workflow's shim to latest
gh aw update pr-review

# Update all workflows
gh aw update
```

`gh aw update` does a 3-way merge preserving your customizations. Shared imports (prompts, tools, formatting) update automatically on recompile — you only need `gh aw update` when the shim itself changes.
