---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/pr-checks-fix.md
description: "Analyze failed PR checks and optionally push fixes"
imports:
  - gh-aw-workflows/pr-checks-fix-rwxp.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  workflow_run:
    workflows: ["CI", "Build", "Test"]
    types: [completed]
concurrency:
  group: pr-checks-fix-${{ github.event.workflow_run.id }}
  cancel-in-progress: false
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  add-comment:
    max: 3
timeout-minutes: 30
# Add setup steps to install tools the agent needs, e.g.:
# steps:
#   - uses: actions/setup-go@v5
#     with:
#       go-version: '1.23'
---

<!-- Add prompt additions here (appended after the imported prompt) -->
