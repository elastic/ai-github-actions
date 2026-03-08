---
inlined-imports: true
name: "Mention in Issue by ID"
description: "AI assistant for a specific issue ID — answer questions, debug, and create PRs on demand"
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
    group: "gh-aw-copilot-${{ github.workflow }}-mention-issue-by-id-${{ inputs.target-issue-number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      target-issue-number:
        description: "Issue number to target"
        type: string
        required: true
      prompt:
        description: "Prompt for the agent"
        type: string
        required: true
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
concurrency:
  group: ${{ github.workflow }}-mention-issue-by-id-${{ inputs.target-issue-number }}
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
  add-comment:
    target: "${{ inputs.target-issue-number }}"
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

# Issue Assistant by ID

Assist with issue #${{ inputs.target-issue-number }} on ${{ github.repository }}.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ inputs.target-issue-number }}
- **Request**: "${{ inputs.prompt }}"

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, comment on the targeted issue, create pull requests, create issues
- **CANNOT**: Directly push or commit to the repository - use `ready_to_make_pr` then `create_pull_request` to propose changes

When creating pull requests, make the changes in the workspace first, call `ready_to_make_pr`, then use `create_pull_request` - branches are managed automatically.

## Instructions

1. Read issue #${{ inputs.target-issue-number }} first to understand the full thread and current context.
2. Handle the request in `${{ inputs.prompt }}` with focused investigation and evidence from the codebase.
3. Do not comment on any issue except #${{ inputs.target-issue-number }}.
4. Use safe outputs only against issue #${{ inputs.target-issue-number }} when commenting.
5. If asked to implement changes, make edits in the workspace, call `ready_to_make_pr`, then use `create_pull_request`.
6. If no code or PR action is needed, call `add_comment` with a concise, actionable response.

${{ inputs.additional-instructions }}
