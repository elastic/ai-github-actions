---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/bug-hunter.md
description: "Find a reproducible, user-impacting bug and file a report issue"
imports:
  - gh-aw-workflows/bug-hunter-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "daily around 11:00 on weekdays"
  workflow_dispatch:
concurrency:
  group: bug-hunter
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
    title-prefix: "[bug-hunter] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
