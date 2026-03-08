---
inlined-imports: true
name: "Plan"
description: "Generate implementation plans from issue comments and create follow-up issues/sub-issues"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-issue.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-plan-${{ github.event.issue.number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
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
      allowed-bot-users:
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      create-issue-max:
        description: "Maximum number of issues the agent can create per run"
        type: string
        required: false
        default: "5"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  reaction: "eyes"
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-plan-${{ github.event.issue.number }}
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, actions]
  bash: true
  web-fetch:
safe-outputs:
  activation-comments: false
  create-issue:
    max: ${{ inputs.create-issue-max }}
strict: false
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# Plan Assistant

Assist with implementation planning on ${{ github.repository }} from issue comments.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}
- **Request**: "${{ steps.sanitized.outputs.text }}"

## Constraints

- **CAN**: Read files, search code, run tests and commands, post issue comments, create new issues/sub-issues.
- **CANNOT**: Directly push code or create pull requests from this workflow.

## Instructions

Understand the request, investigate the codebase, and produce a concrete implementation plan.

### Step 1: Gather Context

1. Read the full issue thread and the request comment.
2. If related issues or PRs are referenced, call `issue_read` / `pull_request_read` with method `get` for each relevant item.
3. Use `grep` and file reading to inspect the relevant code paths.

### Step 2: Investigate and Plan

1. Validate current behavior by running relevant existing commands when useful (tests/lint/build).
2. Form a concrete recommendation with clear implementation steps.
3. If work should be split, create follow-up issues with `create_issue`.
4. For sub-issues, set the `parent` field in `create_issue`.

### Step 3: Post Response

Call `add_comment` with a concise planning response that includes:

1. **Recommendation** — The best implementation approach.
2. **Findings** — Evidence with file paths and line numbers.
3. **Verification** — Commands run and outcomes.
4. **Detailed Action Plan** — Ordered, actionable steps.
5. **Related Items** — Relevant issues, PRs, and files.

Use `<details>` and `<summary>` for long sections.

${{ inputs.additional-instructions }}
