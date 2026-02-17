---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/downstream-health.md
description: "Monitor downstream repositories using AI workflows and report quality issues"
imports:
  - gh-aw-workflows/downstream-health-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "0 10 * * *"  # Daily at 10:00 UTC
  workflow_dispatch:
concurrency:
  group: downstream-health
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
    title-prefix: "[downstream-health] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

<!-- Add prompt additions here (appended after the imported prompt) -->
