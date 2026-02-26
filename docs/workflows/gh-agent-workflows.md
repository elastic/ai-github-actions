# Elastic AI Software Factory (GitHub Agent Workflows)

Elastic AI Software Factory is built on GitHub Agent Workflows with safe-output guardrails. Engine and model are configurable per workflow, and updates are delivered via the `v0` tag.

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

## Recommended workflow sets

The quick setup script includes two opinionated sets:

- **Starter repo operations set (default):** `pr-review`, `issue-triage`, `mention-in-issue`, `mention-in-pr`, `pr-actions-detective`
- **Continuous improvement add-ons (`--continuous-improvement`):** `bug-hunter`, `bug-exterminator`, `code-simplifier`, `docs-patrol`, `newbie-contributor-patrol`, `small-problem-fixer`, `stale-issues`, `test-improver`, `breaking-change-detector`, `code-duplication-detector`, `update-pr-body`

## Available workflows

### Base workflows

Two generic base workflows let you build custom detectors and fixers without writing a full workflow from scratch. Provide your domain-specific instructions via `additional-instructions`:

| Workflow | Role | Output |
| --- | --- | --- |
| [Scheduled Audit](gh-agent-workflows/scheduled-audit.md) | Detect issues and file reports | `create-issue` |
| [Scheduled Fix](gh-agent-workflows/scheduled-fix.md) | Fix reported issues | `create-pull-request` |

These pair together: a Scheduled Audit finds problems, a Scheduled Fix resolves them. The specialized workflows below are built on top of these base fragments.

### Human-coordinated workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| [Docs PR Review](gh-agent-workflows/docs-pr-review.md) | `/docs-review` on PRs | Review docs for style guide, `applies_to`, and consistency |
| [Plan](gh-agent-workflows/plan.md) | `/plan` in issues | Triage-style planning from comments with optional issue/sub-issue creation |
| [Mention in Issue](gh-agent-workflows/mention-in-issue.md) | `/ai` in issues | Answer questions, debug, create PRs |
| [Mention in PR](gh-agent-workflows/mention-in-pr.md) | `/ai` in PRs | Review, fix code, push changes |
| [PR Actions Fixer](gh-agent-workflows/pr-actions-fixer.md) | Manual (workflow_dispatch) | Opt-in fixes for failed PR checks |

### Event-driven workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| [Dependency Review](gh-agent-workflows/dependency-review.md) | Dependabot/Renovate PRs | Analyze dependency updates for commit verification, breaking changes, and risk |
| [Duplicate Issue Detector](gh-agent-workflows/duplicate-issue-detector.md) | New issues | Detect duplicate issues and comment with links |
| [Issue Triage](gh-agent-workflows/issue-triage.md) | New issues | Investigate and provide implementation plans |
| [Issue Fixer](gh-agent-workflows/issue-fixer.md) | New issues | Triage plus automatic draft PR for straightforward fixes |
| [PR Actions Detective](gh-agent-workflows/pr-actions-detective.md) | Failed PR checks | Diagnose failures and recommend fixes |
| [PR Buildkite Detective](gh-agent-workflows/pr-buildkite-detective.md) | Failed PR checks | Diagnose Buildkite failures and recommend fixes |
| [PR Review](gh-agent-workflows/pr-review.md) | PR opened/updated | AI code review with inline comments |
| [PR Review (Fork)](gh-agent-workflows/pr-review-fork.md) | PR opened/updated (`pull_request_target`) | AI code review for fork PRs — **private repos or trusted contributors only** |
| [Update PR Body](gh-agent-workflows/update-pr-body.md) | PR opened / updated / ready for review | Auto-populate PR description from diff and linked issues |

### Scheduled workflows

#### Detector / fixer pairs

Many scheduled workflows follow a **detector / fixer** pattern: the detector finds issues and files reports, then the fixer picks up those reports and creates PRs to resolve them. Install both for a fully autonomous loop, or use the detector alone for human-in-the-loop review.

| Detector | Fixer | Domain |
| --- | --- | --- |
| [Bug Hunter](gh-agent-workflows/bug-hunter.md) | [Bug Exterminator](gh-agent-workflows/bug-exterminator.md) | Reproducible bugs |
| [Code Duplication Detector](gh-agent-workflows/code-duplication-detector.md) | [Code Duplication Fixer](gh-agent-workflows/code-duplication-fixer.md) | Duplicate / clustered code |
| [Docs Patrol](gh-agent-workflows/docs-patrol.md) | — | Stale internal documentation |
| [Docs Patrol External](gh-agent-workflows/docs-patrol-external.md) | — | Stale published Elastic docs |
| [Newbie Contributor Patrol](gh-agent-workflows/newbie-contributor-patrol.md) | [Newbie Contributor Fixer](gh-agent-workflows/newbie-contributor-fixer.md) | Onboarding documentation gaps |
| [Newbie Contributor Patrol External](gh-agent-workflows/newbie-contributor-patrol-external.md) | — | Cross-referencing published docs |
| [Text Auditor](gh-agent-workflows/text-auditor.md) | [Text Beautifier](gh-agent-workflows/text-beautifier.md) | User-facing text quality |

#### Standalone scheduled workflows

| Workflow | Trigger | Description |
| --- | --- | --- |
| [Agent Suggestions](gh-agent-workflows/agent-suggestions.md) | Weekly schedule | Suggest new agent workflows based on repo and downstream needs |
| [Autonomy Atomicity Analyzer](gh-agent-workflows/autonomy-atomicity-analyzer.md) | Weekday schedule | Find patterns that block concurrent development by multiple agents or developers |
| [Breaking Change Detector](gh-agent-workflows/breaking-change-detector.md) | Weekday schedule | Detect undocumented public breaking changes |
| [Code Simplifier](gh-agent-workflows/code-simplifier.md) | Weekday schedule | Simplify overcomplicated code with high-confidence refactors |
| [Downstream Health](gh-agent-workflows/downstream-health.md) | Daily schedule | Monitor downstream repo quality |
| [Flaky Test Investigator](gh-agent-workflows/flaky-test-investigator.md) | Weekday schedule + failed CI runs | Identify repeated flaky failures and file root-cause-first triage reports |
| [Framework Best Practices](gh-agent-workflows/framework-best-practices.md) | Weekday schedule | Find where library-native features could replace hand-rolled solutions |
| [Information Architecture](gh-agent-workflows/information-architecture.md) | Weekday schedule | Audit UI information architecture for navigation, placement, and consistency |
| [Performance Profiler](gh-agent-workflows/performance-profiler.md) | Weekday schedule | Profile performance hotspots |
| [Product Manager Impersonator](gh-agent-workflows/product-manager-impersonator.md) | Weekday schedule | Propose feature ideas from a configurable persona and scope |
| [Project Summary](gh-agent-workflows/project-summary.md) | Daily schedule | Summarize recent activity and priorities |
| [Release Update Check](gh-agent-workflows/release-update.md) | Weekly schedule | Open a PR updating pinned ai-github-actions workflow SHAs and suggest workflow changes |
| [Small Problem Fixer](gh-agent-workflows/small-problem-fixer.md) | Weekday schedule | Fix small, related issues and open a focused PR |
| [Stale Issues](gh-agent-workflows/stale-issues.md) | Weekday schedule | Find resolved issues that can be closed |
| [Test Improver](gh-agent-workflows/test-improver.md) | Weekly schedule | Add targeted tests and clean up redundant coverage |

## Secrets

These workflows require a Copilot PAT stored as `COPILOT_GITHUB_TOKEN`.

1. Create a Copilot PAT with the `copilot-requests` scope (the scope is only available for public repositories).
2. Store it as a repository secret:

````bash
printf '%s' "(pat)" | gh secret set COPILOT_GITHUB_TOKEN --repo OWNER/REPO
````

UI path: Settings → Secrets and variables → Actions → New repository secret.

See the upstream [gh-aw auth docs](https://github.com/github/gh-aw/blob/main/docs/src/content/docs/reference/auth.mdx) for canonical steps.

Some workflows require additional provider-specific secrets (for example, `PR Buildkite Detective` requires `BUILDKITE_API_TOKEN`).

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
2. **Trigger** (`<name>/example.yml`): A plain YAML file that defines the actual event triggers (schedule, PR events, slash commands, etc.) and calls the compiled `.lock.yml` via `uses:`. These serve as both examples for consumers and dogfood for this repo (copied to `.github/workflows/trigger-*.yml` by `scripts/dogfood.sh` for workflows not listed in `EXCLUDED_WORKFLOWS`).

Consumer repos copy a workflow's `example.yml`, change the `uses:` path if needed, and customize the `with:` inputs. Updates propagate automatically when this repo updates the `v0` tag on release.
