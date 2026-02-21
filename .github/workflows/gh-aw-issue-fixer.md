---
inlined-imports: true
name: "Issue Fixer"
description: "Investigate new issues and provide actionable triage analysis with automatic PR creation"
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
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-issue-fixer-${{ github.event.issue.number }}"
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
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  reaction: "eyes"
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: issue-fixer-${{ github.event.issue.number }}
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
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Issue Fixer

Investigate and fix issues in ${{ github.repository }}. Provide actionable analysis with implementation plans. For straightforward fixes, implement and open a draft PR.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}

## Constraints

- **CAN**: Read files, search code, run tests and commands, comment on the issue, and open a draft PR for straightforward fixes.
- This workflow is primarily for investigation and planning. Local file changes are for verification only unless you implement a fix.

## Triage Process

Follow these steps in order.

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Read key repository files (README, CONTRIBUTING, etc.) to understand the project.
3. Search for related issues and PRs (open and closed) that may be relevant. Call `issue_read` with method `get` on the most relevant issues to understand prior discussion, decisions, and whether this is a duplicate.

### Step 2: Investigate the Codebase

1. Read the issue description carefully to understand the request or problem.
2. Explore the relevant parts of the codebase using `grep` and file reading.
3. Run tests or commands in the workspace to verify reported bugs when possible:
   - Run existing tests to confirm reported behavior
   - Execute scripts to understand current behavior
   - Run linters or static analysis if relevant
   - Write small test files to validate findings
   - Always explain what you're testing and why, and include command output in your response
4. If the required change is small, clear, and verifiable, implement it directly and run relevant validation.

### Step 3: Formulate Response

Provide a response with the following sections. Be concise and actionable — no filler or praise.

**Always lead with a tl;dr** — your first sentence should be the most important takeaway.

**Sections:**

1. **Recommendation** — A clear, specific recommendation for how to address the issue. If you cannot recommend a course of action, say so with a reason. "I don't know" is better than a wrong answer.

2. **Findings** — Key facts from your investigation (related code, existing implementations, relevant issues/PRs). Use `<details>` tags for longer content.

3. **Verification** — If you ran tests or commands, include the output. Use `<details>` tags.

4. **Detailed Action Plan** — Step-by-step plan a developer could follow to implement the recommendation (or summary of implemented changes if you completed them). Reference specific files, functions, and line numbers. Use `<details>` tags.

5. **Related Items** — Table of related issues, PRs, files, and web resources.

Use `<details>` and `<summary>` tags for sections that would otherwise make the response too long. Short responses don't need collapsible sections. Your performance is judged by how accurate your findings are — do the investigation required to have high confidence. "I don't know" or "I'm unable to recommend a course of action" is better than a wrong answer.

### Step 4: Post Response

1. Call `add_comment` with your triage response.
2. If you implemented a valid fix with verification, call `create_pull_request` to open a draft PR.

${{ inputs.additional-instructions }}
