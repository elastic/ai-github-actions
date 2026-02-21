---
description: "Detect workflow drift — where one or more workflows have fallen behind a pattern adopted by most others"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  schedule:
    - cron: "daily around 14:00 on weekdays"
  workflow_dispatch:
  roles: [admin, maintainer, write]
  bots:
    - "github-actions[bot]"
concurrency:
  group: gh-aw-workflow-drift
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
network:
  allowed:
    - defaults
    - github
strict: false
safe-outputs:
  messages:
    footer: "---\n[What is this?](https://ela.st/github-ai-tools) | [From workflow: {workflow_name}]({run_url})\n\nGive us feedback! React with 🚀 if perfect, 👍 if helpful, 👎 if not."
  noop:
  create-issue:
    max: 1
    title-prefix: "[workflow-drift] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 90
---

Detect workflow drift — workflows that have fallen behind a structural or naming pattern that the majority of peer workflows already follow.

### Context

This is the `elastic/ai-github-actions` repository. It ships reusable GitHub Actions agent workflows. Each reusable workflow has two files:
- A source definition: `.github/workflows/gh-aw-<name>.md`
- A compiled lock file: `.github/workflows/gh-aw-<name>.lock.yml`

There is also a matching trigger in `gh-agent-workflows/<name>/example.yml` (copied to `.github/workflows/trigger-<name>.yml` for dogfooding), except for internal-only workflows (`upgrade-check`, `downstream-users`, `workflow-drift`, `downstream-health`).

### Data Gathering

1. List all `.github/workflows/gh-aw-*.md` files using `bash` (`ls .github/workflows/gh-aw-*.md`).
2. Read every file in full.
3. List all `gh-agent-workflows/` subdirectories and for each one read `example.yml`.
4. List all `.github/workflows/trigger-*.yml` files and read each one.
5. Check for open issues with the `[workflow-drift]` title prefix to avoid duplicating an already-tracked finding.

### What to Look For

Examine the `.md` workflow source files and their matching trigger/example files. Drift means: **a pattern followed by most workflows is missing from one or a few**.

Look for these specific patterns, checking each one across all workflows:

#### 1. Standard fragment imports (`gh-aw-*.md` files using `workflow_call`)

All `workflow_call` workflows should import these fragments (unless there is a clear reason not to):
- `gh-aw-fragments/formatting.md`
- `gh-aw-fragments/rigor.md`
- `gh-aw-fragments/mcp-pagination.md`

Workflows that output messages to PRs or issues should also import:
- `gh-aw-fragments/messages-footer.md`

Scheduled report workflows (those with `gh-aw-fragments/scheduled-report.md`) should also import:
- `gh-aw-fragments/runtime-setup.md`
- `gh-aw-fragments/elastic-tools.md`

#### 2. Standard `workflow_call` inputs

All `workflow_call` workflows should expose these inputs (unless the workflow has a documented reason to omit one):
- `additional-instructions` — with description, `type: string`, `required: false`, `default: ""`
- `setup-commands` — with description, `type: string`, `required: false`, `default: ""`
- `allowed-bot-users` — with description, `type: string`, `required: false`, `default: "github-actions[bot]"`

Workflows that include `gh-aw-fragments/messages-footer.md` should also expose:
- `messages-footer` — with description, `type: string`, `required: false`, `default: ""`

#### 3. Standard `roles` and `bots` in `on:`

All `workflow_call` workflows should have:
```yaml
roles: [admin, maintainer, write]
bots:
  - "${{ inputs.allowed-bot-users }}"
```

#### 4. Standard `setup-commands` step

All `workflow_call` workflows should have this step at the top of `steps:`:
```yaml
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
```

#### 5. Scheduled-report `create-issue` safe-output settings

Workflows that use `create-issue` as a safe output should have both:
- `close-older-issues: true`
- `expires: 7d`

#### 6. Trigger/example file alignment

For every `.github/workflows/gh-aw-<name>.md` that is not internal-only, there should be:
- A matching `gh-agent-workflows/<name>/` directory with `example.yml` and `README.md`
- A matching `.github/workflows/trigger-<name>.yml`

For every `gh-agent-workflows/<name>/example.yml`, the `uses:` line should reference `elastic/ai-github-actions/.github/workflows/gh-aw-<name>.lock.yml@v0`.

The corresponding `.github/workflows/trigger-<name>.yml` should use `./.github/workflows/gh-aw-<name>.lock.yml` (local reference).

#### 7. `concurrency` group naming

The `concurrency.group` value should match the workflow name (e.g., `docs-drift` for `gh-aw-docs-drift.md`).

### How to Analyze

For each pattern:
1. Identify which workflows follow the pattern (the majority).
2. Identify which workflows deviate.
3. Check if the deviation is intentional or documented (e.g., a comment, a structural reason).
4. Only report deviations where the same pattern is present in ≥ 75% of comparable workflows and absent from < 25%.

**Comparable workflows**: When comparing patterns, only compare workflows of the same type:
- `workflow_call` workflows vs. other `workflow_call` workflows
- `schedule`-triggered workflows vs. other scheduled workflows
- Scheduled-report workflows (those importing `scheduled-report.md`) form their own comparison group

Do not flag a workflow for missing a pattern that doesn't apply to its type.

### What to Skip

- Deviations in internal-only workflows (`upgrade-check`, `downstream-users`, `workflow-drift`, `downstream-health`) — these intentionally differ from the public `workflow_call` pattern
- A missing fragment or input when only 1–2 other workflows have it (not yet a majority pattern)
- Differences already tracked in open issues or recent PRs
- Minor whitespace or comment differences
- Lock file (`.lock.yml`) differences — these are generated and not directly authored

### Quality Gate

**Noop is the expected outcome most days.** Only file an issue if:
- At least one concrete drift instance is found: a specific named workflow is missing a specific named pattern that ≥ 75% of comparable workflows have
- The drift is not already tracked in an open issue or recent PR

### Issue Format

**Issue title:** "Workflow drift detected: [brief summary, e.g., 'missing setup-commands step in 2 workflows']"

**Issue body:**

> Workflow drift detected — the following workflows are missing patterns that most comparable workflows already follow.
>
> ## Drifted Workflows
>
> ### 1. `gh-aw-<name>.md` — [Pattern name]
>
> **Pattern:** [Describe the expected pattern, e.g., "imports `gh-aw-fragments/messages-footer.md`"]
> **Followed by:** [List 2–3 comparable workflows that have it]
> **Missing from:** `gh-aw-<name>.md`
> **Suggested fix:** [Exact change needed]
>
> ### 2. [Next finding...]
>
> ## Suggested Actions
>
> - [ ] [One actionable checkbox per finding]
