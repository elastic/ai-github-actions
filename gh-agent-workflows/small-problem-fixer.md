---
description: "Find small, related issues and open a focused PR"
imports:
  - gh-aw-workflows/small-problem-fixer-rwxp.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "0 12 * * 1-5"
  workflow_dispatch:
concurrency:
  group: small-problem-fixer
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  create-pull-request:
    max: 1
  add-comment:
    max: 3
  noop:
timeout-minutes: 30
---

Find a small, clearly-scoped issue (or a very small set of related issues) and open a single focused PR that fixes it.
