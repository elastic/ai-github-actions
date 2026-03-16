---
inlined-imports: true
name: "PR Conflict Addresser"
description: "Resolve merge conflicts on open PRs when the base branch changes"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/pr-context.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-push-to-pr.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-pr-conflict-addresser-${{ inputs.target-pr-number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      target-pr-number:
        description: "PR number with merge conflicts to resolve"
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
      allowed-bot-users:
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
concurrency:
  group: ${{ github.workflow }}-pr-conflict-addresser-${{ inputs.target-pr-number }}
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, actions]
  bash: true
strict: false
safe-outputs:
  activation-comments: false
  max-patch-size: 10240
  add-comment:
    max: 1
    issues: false
    pull-requests: true
    discussions: false
    target: "${{ inputs.target-pr-number }}"
  push-to-pull-request-branch:
    target: "${{ inputs.target-pr-number }}"
timeout-minutes: 30
steps:
  - name: Checkout target PR branch
    env:
      GH_TOKEN: ${{ github.token }}
      PR_NUMBER: ${{ inputs.target-pr-number }}
    run: |
      set -euo pipefail
      gh pr checkout "$PR_NUMBER"
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
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# PR Conflict Addresser

Resolve merge conflicts on pull request #${{ inputs.target-pr-number }} in ${{ github.repository }}.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ inputs.target-pr-number }}
- **PR context on disk**: `/tmp/pr-context/` — PR metadata, diff, files, reviews, comments, and linked issues are pre-fetched. Use these as your primary source; fall back to API tools only when required data is unavailable.

## Instructions

1. Read `/tmp/pr-context/pr.json` for PR details including `baseRefName` (the target branch).
2. Merge the base branch into the PR branch: `git merge origin/<baseRefName>`.
3. If there are merge conflicts, resolve them by examining the conflicting files and making sensible choices that preserve the intent of both sides.
4. After resolving all conflicts, run any relevant build/lint/test commands to verify the resolution doesn't break anything.
5. Commit the merge result and call `ready_to_push_to_pr`, then `push_to_pull_request_branch`.
6. If conflicts are too complex to resolve automatically, call `add_comment` explaining which files have conflicts and why they need manual resolution.

## Constraints

- **CAN**: Read files, run commands, merge branches, resolve conflicts, push to the PR branch
- **CANNOT**: Push to fork PR branches, rebase or rewrite history, merge the PR itself

${{ inputs.additional-instructions }}
