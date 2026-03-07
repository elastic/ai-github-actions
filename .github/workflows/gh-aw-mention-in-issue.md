---
inlined-imports: true
name: "Mention in Issue"
description: "AI assistant for issues — answer questions, debug, and create PRs on demand"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/playwright-mcp-explorer.md
  - gh-aw-fragments/safe-output-add-comment-issue.md
  - gh-aw-fragments/safe-output-create-pr.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-mention-issue-${{ github.event.issue.number }}"
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
      draft-prs:
        description: "Whether to create pull requests as drafts"
        type: boolean
        required: false
        default: true
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
  reaction: "eyes"
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-mention-issue-${{ github.event.issue.number }}
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
  max-patch-size: 10240
strict: false
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Issue Assistant

Assist with issues on ${{ github.repository }} — answer questions, debug problems, suggest solutions, and create PRs.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}
- **Request**: "${{ steps.sanitized.outputs.text }}"

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, comment on issues, create pull requests, create issues
- **CANNOT**: Directly push or commit to the repository — use `create_pull_request` to propose changes

When creating pull requests, make the changes in the workspace first, then use `create_pull_request` — branches are managed automatically.

## Instructions

Understand the request, investigate the codebase, and respond with a helpful, actionable answer.

### Step 1: Gather Context

1. Read the full issue thread to understand the discussion so far.
2. If the issue references other issues or PRs, call `issue_read` or `pull_request_read` with method `get` on each to understand the broader context.
3. Use `grep` and file reading to explore the relevant parts of the codebase.

### Step 2: Investigate and Respond

Based on the request, do what's appropriate:

- **Answer questions** about the codebase — find the relevant code and explain it
- **Debug reported problems** — reproduce locally, run required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config, and trace the code path
- **Suggest solutions** — provide concrete code examples and implementation guidance
- **Clarify requirements** — ask follow-up questions if the request is ambiguous
- **Create a PR** — if asked to implement something, make the changes in the workspace, then use `create_pull_request` to submit them

When making code changes, identify and run required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config and include results. If required commands cannot be run, explain why.

### Step 3: Post Response

Call `add_comment` with your response. Be concise and actionable — no filler or praise. If the request is unclear, ask clarifying questions rather than guessing.

**Additional tools:**
- `create_pull_request` — create a PR with your changes
- `create_issue` — create a new issue (e.g. to split off sub-tasks)

Unless instructed otherwise, if you do create an issue or a pull request, assign it to the user who requested the change that resulted in the creation of the issue or pull request.

${{ inputs.additional-instructions }}
