---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/agent-efficiency.md
description: "Analyze agent workflow logs for inefficiencies, errors, and prompt improvement opportunities"
imports:
  - gh-aw-workflows/agent-efficiency-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "daily around 16:00 on weekdays"
  workflow_dispatch:
concurrency:
  group: agent-efficiency
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
    title-prefix: "[agent-efficiency] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
