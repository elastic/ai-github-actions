---
description: "Find open issues that appear to already be resolved and recommend closing them"
imports:
  - gh-aw-workflows/stale-issues-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "daily around 15:00 on weekdays"
  workflow_dispatch:
concurrency:
  group: stale-issues
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
    title-prefix: "[stale-issues] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
