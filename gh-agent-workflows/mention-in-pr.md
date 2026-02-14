---
imports:
  - mention-in-pr/prompt.md
engine:
  id: copilot
  model: claude-opus-4.6
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
timeout-minutes: 15
# Add setup steps to install tools the agent needs, e.g.:
# steps:
#   - uses: actions/setup-go@v5
#     with:
#       go-version: '1.23'
---

<!-- Add prompt additions here (appended after the imported prompt) -->
