---
inlined-imports: true
name: "Create Comment On Issue"
description: "Add an AI-generated comment to a specific issue by number"
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
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-create-comment-on-issue-${{ inputs.target-issue-number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      target-issue-number:
        description: "Issue number to comment on"
        type: string
        required: true
      prompt:
        description: "Instructions for what to include in the comment"
        type: string
        required: false
        default: ""
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
  group: ${{ github.workflow }}-create-comment-on-issue-${{ inputs.target-issue-number }}
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
strict: false
safe-outputs:
  activation-comments: false
  max-patch-size: 10240
  add-comment:
    max: 1
    pull-requests: false
    issues: true
    discussions: false
    target: "${{ inputs.target-issue-number }}"
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# Create Comment On Issue

Add a comment to issue #${{ inputs.target-issue-number }} on ${{ github.repository }}.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ inputs.target-issue-number }}
- **Instructions**: "${{ inputs.prompt }}"

## Constraints

- **CAN**: Read files, search code, run commands, comment on the targeted issue
- **CANNOT**: Create pull requests, create issues, or directly push/commit — use `add_comment` to respond

## Instructions

1. Read issue #${{ inputs.target-issue-number }} to understand the context.
2. If the prompt asks for investigation (e.g., code analysis, debugging), explore the codebase as needed.
3. Call `add_comment` with your response. Be concise and actionable.

${{ inputs.additional-instructions }}
