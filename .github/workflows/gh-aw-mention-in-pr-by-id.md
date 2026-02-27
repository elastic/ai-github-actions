---
inlined-imports: true
name: "Mention in PR by ID"
description: "AI assistant for a specific PR ID — review, fix code, and push changes on demand"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/review-process.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-pr.md
  - gh-aw-fragments/safe-output-review-comment.md
  - gh-aw-fragments/safe-output-submit-review.md
  - gh-aw-fragments/safe-output-push-to-pr.md
  - gh-aw-fragments/safe-output-resolve-thread.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-mention-pr-by-id-${{ inputs.target-pr-number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      target-pr-number:
        description: "PR number to target"
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
      create-pull-request-review-comment-max:
        description: "Maximum number of review comments the agent can create per run"
        type: string
        required: false
        default: "30"
      resolve-pull-request-review-thread-max:
        description: "Maximum number of review threads the agent can resolve per run"
        type: string
        required: false
        default: "10"
      github-token-for-extra-empty-commit:
        description: "GitHub token for pushing an extra empty commit to allow workflows to run on bot-created PRs"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: mention-pr-by-id-${{ inputs.target-pr-number }}
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
  add-comment:
    target: "${{ inputs.target-pr-number }}"
  create-pull-request-review-comment:
    target: "${{ inputs.target-pr-number }}"
  submit-pull-request-review:
    target: "${{ inputs.target-pr-number }}"
  push-to-pull-request-branch:
    target: "${{ inputs.target-pr-number }}"
    github-token-for-extra-empty-commit: ${{ inputs.github-token-for-extra-empty-commit }}
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

# PR Assistant by ID

Assist with pull request #${{ inputs.target-pr-number }} on ${{ github.repository }}.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ inputs.target-pr-number }}
- **Request**: "${{ inputs.prompt }}"

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, leave inline review comments, submit reviews, resolve review threads, push to the PR branch (same-repo only)
- **CANNOT**: Push to fork PR branches, merge PRs, delete branches

## Instructions

1. Call `generate_agents_md` to get repository conventions.
2. Call `pull_request_read` with method `get` on PR #${{ inputs.target-pr-number }} to collect PR context.
3. Handle the request in `${{ inputs.prompt }}` with focused changes and evidence.
4. Do not modify, review, comment on, or resolve threads for any PR other than #${{ inputs.target-pr-number }}.
5. Use safe outputs only against PR #${{ inputs.target-pr-number }}.
6. If no code/review action is needed, call `add_comment` with a concise response.

${{ inputs.additional-instructions }}
