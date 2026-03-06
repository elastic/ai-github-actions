---
inlined-imports: true
name: "PR Human Review Labeler"
description: "Evaluate PR blast radius and apply human_required or no_human_required labels"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-pr-human-review-labeler-${{ github.event.pull_request.number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      additional-instructions:
        description: "Repo-specific instructions appended to the agent prompt"
        type: string
        required: false
        default: ""
      setup-commands:
        description: "Shell commands to run before the agent starts (dependency install, build, etc.)"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: ${{ github.workflow }}-pr-human-review-labeler-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, actions]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  noop:
    max: 1
  add-labels:
    max: 2
    target: "${{ github.event.pull_request.number }}"
    allowed:
      - "human_required"
      - "no_human_required"
  remove-labels:
    max: 2
    target: "${{ github.event.pull_request.number }}"
    allowed:
      - "human_required"
      - "no_human_required"
timeout-minutes: 60
steps:
  - name: Ensure classification labels exist
    env:
      GH_TOKEN: ${{ github.token }}
    run: |
      set -euo pipefail
      gh label create human_required --color B60205 --description "PR likely has significant blast radius; human review required." --repo "$GITHUB_REPOSITORY" --force
      gh label create no_human_required --color 0E8A16 --description "PR looks straightforward and low risk." --repo "$GITHUB_REPOSITORY" --force
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# PR Human Review Labeler

Evaluate the pull request and assign exactly one label: `human_required` or `no_human_required`.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} — ${{ github.event.pull_request.title }}

## Goal

Estimate whether this PR has meaningful blast radius and needs explicit human review.

## Instructions

1. Read the full PR details and changed files for #${{ github.event.pull_request.number }}.
2. Classify as `human_required` when the change is risky, complex, broad, under-tested, or likely to impact critical behavior.
3. Classify as `no_human_required` only when the change is straightforward, narrow, and low-risk.
4. Use these risk signals:
   - Broad scope (many files/modules/services)
   - High churn, complex logic, migrations, or API/behavior changes
   - Security/auth/permissions/build or workflow changes
   - Missing or weak tests for substantive code changes
   - Non-trivial operational impact (deploy/runtime/config blast radius)
5. Before adding a label, remove the opposite label if present so only one classification label remains.
6. Apply exactly one of:
   - `add_labels` with `human_required`
   - `add_labels` with `no_human_required`
7. If context is insufficient, default to `human_required` (conservative).
8. Call `noop` only if the PR cannot be evaluated at all.

${{ inputs.additional-instructions }}
