---
inlined-imports: true
name: "Create PR From Issue"
description: "Implement an issue and open a pull request"
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
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-create-pr-from-issue-${{ inputs.target-issue-number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      target-issue-number:
        description: "Issue number to implement"
        type: string
        required: true
      prompt:
        description: "Additional implementation instructions"
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
  group: ${{ github.workflow }}-create-pr-from-issue-${{ inputs.target-issue-number }}
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
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Create PR From Issue

Implement issue #${{ inputs.target-issue-number }} on ${{ github.repository }} and open a pull request.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ inputs.target-issue-number }}
- **Additional request**: "${{ inputs.prompt }}"

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, comment on the targeted issue, create pull requests
- **CANNOT**: Directly push or commit to the repository — use `ready_to_make_pr` then `create_pull_request` to propose changes

## Instructions

1. Read issue #${{ inputs.target-issue-number }} first to understand requirements and acceptance criteria.
2. Investigate the relevant code paths and implement a focused fix for the issue.
3. Run required repo checks (lint/build/test) relevant to your change. If required commands cannot run, explain why and do not open a PR.
4. Call `ready_to_make_pr` and apply its checklist.
5. Call `create_pull_request` with a clear title/body that references and closes issue #${{ inputs.target-issue-number }}.
6. If implementation is blocked or unclear, call `add_comment` on the issue with a concise status update and concrete next step.

${{ inputs.additional-instructions }}
