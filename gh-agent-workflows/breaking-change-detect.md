---
description: "Detect undocumented breaking changes in public interfaces"
imports:
  - gh-aw-workflows/breaking-change-detect-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "0 13 * * 1-5"
  workflow_dispatch:
concurrency:
  group: breaking-change-detect
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
    title-prefix: "[breaking-change] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
