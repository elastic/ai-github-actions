---
description: "Analyze Go code for semantic function clustering and refactoring opportunities"
imports:
  - gh-aw-workflows/semantic-function-clustering-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "0 12 * * 1-5"
  workflow_dispatch:
concurrency:
  group: semantic-function-clustering
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
    title-prefix: "[refactor] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
