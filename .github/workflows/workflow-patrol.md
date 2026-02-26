---
inlined-imports: true
name: "Internal: Workflow Patrol"
description: "Detect workflow drift — where one or more workflows have fallen behind a pattern adopted by most others"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/best-of-three-investigation.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  schedule:
    - cron: "daily around 14:00 on weekdays"
  workflow_dispatch:
    inputs:
      title-prefix:
        description: "Title prefix for created issues"
        required: false
        default: "[workflow-patrol]"
  roles: [admin, maintainer, write]
  bots:
    - "github-actions[bot]"
concurrency:
  group: workflow-patrol
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
  noop:
  create-issue:
    max: 1
    title-prefix: "[workflow-patrol] "
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
---

Detect workflow drift — workflows that have fallen behind a structural pattern that most of their peers already follow. The typical cause is two PRs open side-by-side: one lands a refactor across all workflows, the other adds a new workflow that misses the refactor.

### Context

This is the `elastic/ai-github-actions` repository. It ships reusable GitHub Actions agent workflows. The file layout for each public workflow is:

- **Source**: `.github/workflows/gh-aw-<name>.md` (frontmatter + prompt)
- **Compiled**: `.github/workflows/gh-aw-<name>.lock.yml` (generated — ignore for drift)
- **Trigger**: `.github/workflows/trigger-<name>.yml` (dogfood caller)
- **Consumer example**: `gh-agent-workflows/<name>/example.yml` (external caller template)
- **README**: `gh-agent-workflows/<name>/README.md`

Internal-only workflows (`upgrade-check`, `downstream-users`, `workflow-patrol`) intentionally skip the trigger/example/README files and use `schedule`/`workflow_dispatch` instead of `workflow_call`. Exclude them from comparisons against public workflows.

Shared fragments live in `.github/workflows/gh-aw-fragments/`.

### Instructions

#### Step 1: Read everything

1. Read all `.github/workflows/gh-aw-*.md` files (the workflow sources — not the lock files).
2. Read all `.github/workflows/gh-aw-fragments/*.md` files (the shared fragments).
3. Read all `.github/workflows/trigger-*.yml` files and all `gh-agent-workflows/*/example.yml` files.
4. Check for open issues with the `[workflow-patrol]` title prefix to avoid duplicating already-tracked findings.

#### Step 2: Discover majority patterns

For each structural dimension of the workflow sources, determine what the majority convention is. Examine at least:

- **Frontmatter fields**: Which imports, inputs, secrets, roles, bots, permissions, tools, network allows, safe-outputs, and steps appear? What values do they use?
- **Prompt structure**: What sections and headings are common? What ordering is typical?
- **Trigger/example files**: Do they exist for every public workflow? Are the `uses:` references consistent?
- **Naming conventions**: Do concurrency groups, safe-output configurations, and file names follow a consistent scheme?

You are not limited to these dimensions. If you notice any other structural pattern that most workflows share, include it.

#### Step 3: Identify outliers

For each pattern you discovered, find workflows that deviate. A deviation is drift only if:

- The pattern is followed by **>= 75%** of comparable workflows (compare `workflow_call` workflows against each other, scheduled workflows against each other)
- The deviation is not obviously intentional (e.g., a workflow that genuinely doesn't need a particular input or fragment)
- The finding is not already tracked in an open `[workflow-patrol]` issue

#### Step 4: Report or noop

**Noop is the expected outcome most days.** Only file an issue if you found at least one concrete drift instance.

If filing an issue, use this structure:

**Title**: "Workflow drift detected: [brief summary]"

**Body**:

For each finding:
- Which workflow(s) deviate
- What the majority pattern is (with 2–3 examples of workflows that follow it)
- What specifically is missing or different
- The suggested fix

End with a checklist of actionable items, one per finding.
