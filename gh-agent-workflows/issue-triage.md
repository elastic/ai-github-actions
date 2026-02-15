---
description: "Investigate new issues and provide actionable triage analysis"
imports:
  - issue-triage/rwx.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  issues:
    types: [opened]
  reaction: "eyes"
concurrency:
  group: issue-triage-${{ github.event.issue.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
bots:
  - "github-actions[bot]"
safe-outputs:
  add-comment:
    max: 1
timeout-minutes: 30
# Add setup steps to install tools the agent needs, e.g.:
# steps:
#   - uses: actions/setup-go@v5
#     with:
#       go-version: '1.23'
---

<!-- Add prompt additions here (appended after the imported prompt) -->
