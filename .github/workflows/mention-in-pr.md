---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/mention-in-pr.md
description: "AI assistant for PRs — review, fix code, and push changes via /ai"
imports:
  - gh-aw-workflows/mention-in-pr-rwxp.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  slash_command:
    name: ai
    events: [pull_request, pull_request_comment, pull_request_review_comment]
  reaction: "eyes"
concurrency:
  group: mention-pr-${{ github.event.issue.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  add-comment:
    max: 3
timeout-minutes: 30
# Add setup steps to install tools the agent needs, e.g.:
# steps:
#   - uses: actions/setup-go@v5
#     with:
#       go-version: '1.23'
---

<!-- Add prompt additions here (appended after the imported prompt) -->
