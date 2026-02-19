---
description: "Investigate new issues and optionally implement fixes with PRs"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment.md
  - gh-aw-fragments/safe-output-create-pr.md
engine:
  id: copilot
  model: gpt-5.3-codex
  concurrency:
    group: "gh-aw-copilot-issue-triage-pr-${{ github.event.issue.number }}"
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
      automatic-prs:
        description: "Allow the agent to create a PR when implementation is straightforward (default: false)"
        type: string
        required: false
        default: "false"
      draft-prs:
        description: "Create PRs as draft (default: true)"
        type: string
        required: false
        default: "true"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  reaction: "eyes"
concurrency:
  group: issue-triage-pr-${{ github.event.issue.number }}
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
bots:
  - "github-actions[bot]"
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Issue Triage Agent (Optional PRs)

Triage new issues in ${{ github.repository }} and provide actionable analysis, with optional PR creation controlled by workflow input.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}
- **Automatic PRs Enabled**: `${{ inputs.automatic-prs }}`

## Constraints

- **CAN**: Read files, search code, run tests and commands, and comment on the issue.
- **OPTIONAL**: If `automatic-prs` is `true`, you may implement straightforward fixes and call `create_pull_request` once.
- **DEFAULT**: If `automatic-prs` is not `true`, this is investigation and planning only and your only output is an issue comment.

## Triage Process

Follow these steps in order.

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Read key repository files (README, CONTRIBUTING, etc.) to understand the project.
3. Search for related issues and PRs (open and closed) that may be relevant. Call `issue_read` with method `get` on the most relevant issues to understand prior discussion, decisions, and whether this is a duplicate.

### Step 2: Investigate the Codebase

1. Read the issue description carefully to understand the request or problem.
2. Explore the relevant parts of the codebase using `grep` and file reading.
3. Run tests or commands in the workspace to verify reported bugs when possible.
4. If `automatic-prs` is `true` and the required change is small, clear, and verifiable, implement it directly and run relevant validation before proposing a PR.

### Step 3: Formulate Response

Provide a concise response with:

1. **Recommendation** — clear recommendation and rationale.
2. **Findings** — key facts from investigation (use `<details>` for long sections).
3. **Verification** — command/test output when run.
4. **Detailed Action Plan** — concrete implementation plan (or summary of implemented changes if you completed them).
5. **Related Items** — table of related issues, PRs, files, and resources.

Always lead with a tl;dr. If confidence is low, say so explicitly.

### Step 4: Post Response

1. Call `add_comment` with your response.
2. If `automatic-prs` is `true` **and** you completed a valid implementation with verification, call `create_pull_request`.

${{ inputs.additional-instructions }}
