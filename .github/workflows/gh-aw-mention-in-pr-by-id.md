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
  - gh-aw-fragments/pr-context.md
  - gh-aw-fragments/review-process.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/pick-three-keep-many.md
  - gh-aw-fragments/safe-output-code-review.md
  - gh-aw-fragments/playwright-mcp-explorer.md
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
    group: "gh-aw-copilot-${{ github.workflow }}-mention-pr-by-id-${{ inputs.target-pr-number }}"
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
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
concurrency:
  group: ${{ github.workflow }}-mention-pr-by-id-${{ inputs.target-pr-number }}
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
    target: "${{ inputs.target-pr-number }}"
  create-pull-request-review-comment:
    target: "${{ inputs.target-pr-number }}"
  submit-pull-request-review:
    target: "${{ inputs.target-pr-number }}"
  push-to-pull-request-branch:
    target: "${{ inputs.target-pr-number }}"
    github-token-for-extra-empty-commit: ${{ secrets.EXTRA_COMMIT_GITHUB_TOKEN }}
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
- **PR context on disk**: `/tmp/pr-context/` — PR metadata, diff, files, reviews, comments, and linked issues are pre-fetched. Use these as your primary source; fall back to API tools only when required data is unavailable.
- **Request**: "${{ inputs.prompt }}"

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, leave inline review comments, submit reviews, resolve review threads, push to the PR branch (same-repo only)
- **CANNOT**: Push to fork PR branches, merge PRs, delete branches

## Instructions

1. Read `/tmp/pr-context/pr.json` for PR details. Read `/tmp/pr-context/README.md` for a manifest of all pre-fetched PR context.
2. Handle the request in `${{ inputs.prompt }}` with focused changes and evidence.
3. Do not modify, review, comment on, or resolve threads for any PR other than #${{ inputs.target-pr-number }}.
4. Use safe outputs only against PR #${{ inputs.target-pr-number }}.
5. If no code/review action is needed, call `add_comment` with a concise response.

**If asked to review the PR:**
- Call `ready_to_code_review` to prepare the review approach based on PR size.
- Read `/tmp/pr-context/reviews.json` and `/tmp/pr-context/review_comments.json` to check prior reviews and existing threads — do not duplicate feedback.
- Read `/tmp/pr-context/agent-review.md` for the review approach and follow it. For small PRs, review directly. For medium/large PRs, spawn the specified number of `code-review` sub-agents in parallel (each reads its `/tmp/pr-context/subagent-*.md` instruction file).
- When sub-agents return findings, merge and deduplicate per the Pick Three, Keep Many process. Then verify each surviving finding before leaving a comment:
  1. **Read the file and surrounding context** — open the full file, not just the diff.
  2. **Construct a concrete failure scenario** — what specific input or state causes the bug? If you cannot describe one, drop the finding.
  3. **Challenge the finding** — would a senior engineer familiar with this codebase agree this is a real issue? If unsure, drop it.
  4. **Check existing threads** — if this issue was already flagged (resolved or unresolved), do not duplicate.
- Leave inline comments per the **Code Review Reference** for each finding that survives verification. Then call `submit_pull_request_review`.
- **Bot-authored PRs**: If the PR author is `github-actions[bot]`, submit a `COMMENT` review only — `APPROVE` and `REQUEST_CHANGES` will fail.

**If asked to fix code or address review feedback:**
- Read `/tmp/pr-context/unresolved_threads.json` to identify open review feedback.
- Implement the requested code changes and run relevant lint/build/test commands for the modified area.
- Call `ready_to_push_to_pr` to confirm the branch is safe to push.
- Use `push_to_pull_request_branch` to push your changes once.
- Resolve every thread that is fully addressed by your changes using `resolve_pull_request_review_thread` and the thread GraphQL node ID (`id`, e.g., `PRRT_kwDO...`).
- Do **not** resolve threads you disagreed with, skipped, or only partially addressed; instead, leave a `reply_to_pull_request_review_comment` explaining status when needed.
- **Important completion step**: feedback is not fully complete until fully addressed threads are marked resolved via safe output.
- If `resolve_pull_request_review_thread` fails for fully addressed threads, call `add_comment` listing the thread IDs and failure reason.

${{ inputs.additional-instructions }}
