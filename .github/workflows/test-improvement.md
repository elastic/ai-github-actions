---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/test-improvement.md
description: "Add focused tests for under-tested code and clean up redundant tests"
imports:
  - gh-aw-workflows/test-improvement-rwxp.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "weekly on monday around 09:00"
  workflow_dispatch:
concurrency:
  group: test-improvement
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  noop:
timeout-minutes: 45
---

<!-- Add prompt additions here (appended after the imported prompt) -->
