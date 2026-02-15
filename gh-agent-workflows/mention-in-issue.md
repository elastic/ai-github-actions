---
description: "AI assistant for issues — answer questions, debug, and create PRs via /ai"
imports:
  - gh-aw-workflows/mention-in-issue-rwxp.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  slash_command:
    name: ai
    events: [issues, issue_comment]
  reaction: "eyes"
concurrency:
  group: mention-issue-${{ github.event.issue.number }}
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
