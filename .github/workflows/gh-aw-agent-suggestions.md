---
description: "Suggest new agent workflows based on repo needs and downstream activity"
timeout-minutes: 60
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  workflow_call:
    inputs:
      additional-instructions:
        description: "Repo-specific instructions appended to the agent prompt"
        type: string
        required: false
        default: ""
      setup-commands:
        description: "Shell commands to run before the agent starts (dependency install, build, etc.)"
        type: string
        required: false
        default: ""
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: agent-suggestions
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
    - go
    - node
    - python
    - ruby
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  noop:
  create-issue:
    max: 1
    title-prefix: "[agent-suggestions] "
    close-older-issues: true
    expires: 7d
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Suggest new agent workflows that would materially improve software development for this repository and its downstream users.

## Report Assignment

### Data Gathering

1. **Inventory existing workflows**
   - Read `README.md` and `gh-agent-workflows/README.md` to list current workflows, triggers, and scopes.
   - Skim `gh-agent-workflows/` directory names to confirm what already exists.

2. **Check for duplicates or in-flight work**
   - Search open issues for existing requests: `repo:{owner}/{repo} is:issue is:open (agent OR workflow OR automation)`.
   - Search open PRs for new workflows: `repo:{owner}/{repo} is:pr is:open (agent OR workflow)`.
   - Search past reports: `repo:{owner}/{repo} is:issue in:title "[agent-suggestions]"`.

3. **Evaluate software development needs in this repo**
   - Review open issues and PRs updated in the last 30 days for recurring work patterns (maintenance, docs, testing, releases, dependency updates).
   - Identify any recurring tasks that are not already covered by existing agents.

4. **Evaluate downstream activity**
   - Discover downstream repos using these workflows:
     `github-search_code: query="org:elastic elastic/ai-github-actions/.github/workflows/gh-aw- language:yaml"`.
   - For 3-5 active downstream repos, review open issues and PRs updated in the last 30 days.
   - Look for recurring needs that could be automated by a new agent workflow.

### What to Suggest

- Propose **1–3** new workflows only when there is strong evidence of a gap.
- Each suggestion must include:
  - **Proposed workflow name**
  - **Trigger** (schedule, issue/PR events, slash command)
  - **Purpose and scope**
  - **Proposed safe outputs** (issue, PR, comment)
  - **Evidence** (links to issues/PRs or downstream repo activity)
  - **Why it is not already covered** by existing workflows

### Noop

If no strong, actionable gaps are found, call `noop` with:
"Agent suggestions skipped — no clear, actionable gaps found in current workflows or downstream needs".

### Issue Format

**Issue title:** Agent suggestions - YYYY-MM-DD

**Issue body:**

> ## Agent Suggestions
> **Date:** YYYY-MM-DD
>
> ### 1. [Proposed workflow name]
> **Trigger:** [event or schedule]
> **Purpose:** [what it does and why it helps]
> **Proposed safe outputs:** [create-issue/create-pull-request/add-comment]
> **Evidence:** [links]
> **Why not covered already:** [short explanation]
>
> ### 2. [Next suggestion if any]
>
> ## Duplicate Checks
> - [Links to open issues/PRs reviewed]
>
> ## Downstream Signals
> - [Repo + issue/PR links]
>
> ## Suggested Next Steps
> - [ ] [Actionable follow-up]

${{ inputs.additional-instructions }}
