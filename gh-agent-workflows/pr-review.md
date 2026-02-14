---
imports:
  - pr-review/prompt.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  pull_request:
    types: [opened, synchronize, reopened]
concurrency:
  group: pr-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  contents: read
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
