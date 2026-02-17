---
description: "Find small, related issues and open a focused PR"
imports:
  - gh-aw-workflows/small-problem-fixer-rwxp.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "daily around 12:00 on weekdays"
  workflow_dispatch:
concurrency:
  group: small-problem-fixer
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  noop:
timeout-minutes: 30
# Add setup steps to install tools the agent needs, e.g.:
# steps:
#   - uses: actions/setup-go@v5
#     with:
#       go-version: '1.23'
---

<!-- Add prompt additions here (appended after the imported prompt) -->
