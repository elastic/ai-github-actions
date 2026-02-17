---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/pr-review.md
description: "AI code review with inline comments on pull requests"
imports:
  - path: gh-aw-workflows/pr-review-rwx.md
    inputs:
      intensity: "balanced"  # conservative | balanced | aggressive
      minimum_severity: "low"  # critical | high | medium | low | nitpick
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review, labeled, unlabeled]
# Skip draft PRs and allow opt-out with the skip-auto-pr-review label.
if: >-
  github.event.pull_request.draft == false &&
  !contains(github.event.pull_request.labels.*.name, 'skip-auto-pr-review')
concurrency:
  group: pr-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  contents: read
  pull-requests: read
  issues: read
strict: false
roles: [admin, maintainer, write]
bots:
  - "github-actions[bot]"
timeout-minutes: 30
# Add setup steps to install tools the agent needs, e.g.:
# steps:
#   - uses: actions/setup-go@v5
#     with:
#       go-version: '1.23'
---

<!-- Add prompt additions here (appended after the imported prompt) -->
