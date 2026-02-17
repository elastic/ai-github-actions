---
description: "Detect code changes that require documentation updates and file issues"
imports:
  - gh-aw-workflows/docs-drift-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "daily around 14:00 on weekdays"
  workflow_dispatch:
concurrency:
  group: docs-drift
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  create-issue:
    max: 1
    title-prefix: "[docs-drift] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
