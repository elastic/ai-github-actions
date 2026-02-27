---
inlined-imports: true
name: "PR Review"
description: "AI code review with inline comments on pull requests"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/review-process.md
  - gh-aw-fragments/review-examples.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-review-comment.md
  - gh-aw-fragments/safe-output-submit-review.md
  - gh-aw-fragments/pick-three-keep-many.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-pr-review-${{ github.event.pull_request.number }}"
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
      intensity:
        description: "Review intensity: conservative, balanced, or aggressive"
        type: string
        required: false
        default: "balanced"
      minimum_severity:
        description: "Minimum severity for inline comments: critical, high, medium, low, or nitpick. Issues below this threshold go in a collapsible section of the review body instead."
        type: string
        required: false
        default: "low"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      create-pull-request-review-comment-max:
        description: "Maximum number of review comments the agent can create per run"
        type: string
        required: false
        default: "30"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: pr-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, actions]
  bash: true
  web-fetch:
safe-outputs:
  activation-comments: false
strict: false
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# PR Review Agent

Review pull requests in ${{ github.repository }} and provide actionable feedback via inline review comments on specific code lines.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} — ${{ github.event.pull_request.title }}

## Constraints

This workflow is read-only. You can read files, search code, run commands, and interact with PRs and issues — but your only outputs are inline review comments and a review submission.

## Review Process

Follow these steps in order.

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. Use these as additional review criteria throughout the review. If this fails, continue without it.
2. Call `pull_request_read` with method `get` on PR #${{ github.event.pull_request.number }} to get the full PR details (author, description, branches).
3. If the PR description references issues (e.g., "Fixes #123", "Closes #456"), call `issue_read` with method `get` on each linked issue to understand the motivation and acceptance criteria.
4. Call `pull_request_read` with method `get_review_comments` to check existing review threads. Note which files already have threads and whether threads are resolved, unresolved, or outdated.
5. Call `pull_request_read` with method `get_reviews` to see prior review submissions from this bot. Do not repeat points already made in prior reviews.

### Step 2: Review Each File

Follow the **Pick Three, Keep Many** process above — spawn 3 `code-review` sub-agents to review the PR diff in parallel from different angles (e.g., security/input validation, logic correctness/edge cases, error handling/resource management). Include the full PR diff, file contents, repo conventions from `generate_agents_md`, the **Code Review Reference** criteria below, existing review threads, and the severity/intensity settings in each sub-agent prompt. After merging and deduplicating their findings, leave your own inline comments using the **Code Review Reference** format below.

### Step 3: Submit the Review

**Skip if nothing new:** If you left zero inline comments during this review AND your verdict would be the same as the most recent review from this bot (compare against `get_reviews` from Step 1), call `noop` with a message like "No new findings — prior review still applies" and stop. Do not submit a redundant review.

After reviewing ALL files and leaving inline comments, step back and consider the PR as a whole. Call **`submit_pull_request_review`** with:
- The review type (REQUEST_CHANGES, COMMENT, or APPROVE)
- A review body that is **only the verdict and only if the verdict is not APPROVE**. If you have cross-cutting feedback that spans multiple files or cannot be expressed as inline comments, include it here. Otherwise, leave the review body empty — your inline comments already contain the detail.

**Bot-authored PRs:** If the PR author is `github-actions[bot]`, you can only submit a `COMMENT` review — `APPROVE` and `REQUEST_CHANGES` will fail because GitHub does not allow bot accounts to approve or request changes on their own PRs. Use `COMMENT` and state your verdict in the review body instead.

**Do NOT** describe what the PR does, list the files you reviewed, summarize inline comments, or restate prior review feedback. The PR author already knows what their PR does. Your inline comments already contain all the detail. The review body exists solely to communicate the approve/request-changes decision and important/critical feedback that cannot be covered in inline comments.

If you have no issues, or you have only provided NITPICK and LOW issues, submit an APPROVE review. Otherwise, submit a REQUEST_CHANGES review.

## Review Settings

- **Intensity**: `${{ inputs.intensity }}`
- **Minimum inline severity**: `${{ inputs.minimum_severity }}`

These override the defaults defined in the Code Review Reference below.

${{ inputs.additional-instructions }}
