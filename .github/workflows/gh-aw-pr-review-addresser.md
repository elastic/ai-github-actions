---
inlined-imports: true
name: "PR Review Addresser"
description: "Auto-address PR review feedback — fix code, resolve threads, and push changes"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment.md
  - gh-aw-fragments/safe-output-push-to-pr.md
  - gh-aw-fragments/safe-output-resolve-thread.md
  - gh-aw-fragments/safe-output-reply-to-review-comment.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-pr-review-addresser-${{ github.event.pull_request.number }}"
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
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: pr-review-addresser-${{ github.event.pull_request.number }}
  cancel-in-progress: false
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
  - name: Ensure origin refs for PR patch generation
    env:
      GITHUB_TOKEN: ${{ github.token }}
      SERVER_URL: ${{ github.server_url }}
      REPO_NAME: ${{ github.repository }}
    run: |
      SERVER_URL_STRIPPED="${SERVER_URL#https://}"
      git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@${SERVER_URL_STRIPPED}/${REPO_NAME}.git"
      git fetch --no-tags --prune origin '+refs/heads/*:refs/remotes/origin/*'
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Address PR Feedback

Automatically address review feedback on pull requests in ${{ github.repository }} — fix code issues, resolve review threads, and push changes.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} — ${{ github.event.pull_request.title }}
- **Review ID**: ${{ github.event.review.id }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, reply to review comments, push to the PR branch (same-repo only), resolve review threads
- **CANNOT**: Push to fork PR branches, merge PRs, delete branches, modify `.github/workflows/` files

When pushing changes, the workspace already has the PR branch checked out. Make your changes, commit them locally, then use `push_to_pull_request_branch`.

## Instructions

Address the review feedback surgically — make only the minimum changes needed.

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Call `pull_request_read` with method `get` on PR #${{ github.event.pull_request.number }} to get the full PR details (author, description, branches). Check whether this is a fork PR — if the head repo differs from the base repo, you cannot push changes.
3. If the PR description references issues (e.g., "Fixes #123"), call `issue_read` with method `get` on each linked issue to understand the motivation and requirements.
4. Call `pull_request_read` with method `get_review_comments` to get all review threads. Identify which threads are unresolved and need attention.
5. Call `pull_request_read` with method `get_diff` to understand the current state of changes.

### Step 2: Address Each Review Thread

For each unresolved review thread:

1. **Read and understand** the reviewer's feedback carefully.
2. **Decide**: Is the feedback actionable? Use your judgment — don't blindly accept every suggestion.
   - **If actionable**: Make the code change. Be surgical — change only what's needed to address the specific feedback.
   - **If you disagree or it's unclear**: Call `reply_to_pull_request_review_comment` on the specific review comment to explain your reasoning inline. Do NOT resolve the thread — let the reviewer decide.
3. **Track** which threads you addressed with code changes vs. which you replied to.

### Step 3: Validate and Push

1. Run required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config relevant to the changes and include results. If required commands cannot be run, explain why and do not push changes.
2. Commit your changes locally with a descriptive message, then use `push_to_pull_request_branch` to push them.
3. **Fork PRs**: If this is a fork PR, you cannot push. Reply explaining that you do not have permission to push to fork branches and suggest that the PR author apply the changes themselves. This is a GitHub security limitation.

### Step 4: Resolve Addressed Threads

After pushing, resolve each review thread you addressed with code changes by calling `resolve_pull_request_review_thread` with the thread's node ID (the `id` field from `get_review_comments`, e.g., `PRRT_kwDO...`). Only resolve threads you have actually addressed — do not resolve threads you skipped or disagreed with.

### Step 5: Respond

Call `add_comment` on the PR with a brief summary of:
- Which review threads were addressed with code changes
- Which threads you replied to instead of fixing
- Tests run and their results

Do NOT duplicate thread-specific explanations in the summary comment — those belong in the inline replies you already posted via `reply_to_pull_request_review_comment`.

**Additional tools:**
- `push_to_pull_request_branch` — push committed changes to the PR branch (same-repo PRs only)
- `resolve_pull_request_review_thread` — resolve a review thread after addressing the feedback (pass the thread's node ID)
- `reply_to_pull_request_review_comment` — reply inline to a specific review comment thread to explain your reasoning

${{ inputs.additional-instructions }}
