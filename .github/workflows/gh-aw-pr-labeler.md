---
inlined-imports: true
name: "PR Labeler"
description: "Evaluate a pull request and apply classification labels"
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
    group: "gh-aw-copilot-${{ github.workflow }}-pr-labeler-${{ github.event.pull_request.number }}"
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
      classification-labels:
        description: "Comma-separated list of classification labels the agent may apply"
        type: string
        required: true
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: ${{ github.workflow }}-pr-labeler-${{ github.event.pull_request.number }}
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
    max: 10
    target: "${{ github.event.pull_request.number }}"
  remove-labels:
    max: 10
    target: "${{ github.event.pull_request.number }}"
  steps:
    - name: Pre-sanitize label operations from input allowlist
      uses: actions/github-script@v7
      env:
        ALLOWED_LABELS: ${{ inputs.classification-labels }}
      with:
        script: |
          const fs = require('fs');
          const outputPath = process.env.GH_AW_AGENT_OUTPUT;
          if (!outputPath || !fs.existsSync(outputPath)) {
            core.info('No GH_AW_AGENT_OUTPUT file found; skipping.');
            return;
          }
          const allowed = new Set(
            String(process.env.ALLOWED_LABELS || '')
              .split(',')
              .map((s) => s.trim())
              .filter(Boolean)
          );
          if (allowed.size === 0) {
            core.info('No allowed labels provided; skipping.');
            return;
          }
          const doc = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
          if (!Array.isArray(doc.items)) {
            core.warning('agent output has no items array; skipping.');
            return;
          }
          let removed = 0;
          let dropped = 0;
          doc.items = doc.items.filter((item) => {
            if (
              (item?.type !== 'add_labels' && item?.type !== 'remove_labels') ||
              !Array.isArray(item.labels)
            ) {
              return true;
            }
            const before = item.labels.length;
            item.labels = item.labels
              .map((v) => String(v).trim())
              .filter((v) => v && allowed.has(v));
            removed += Math.max(0, before - item.labels.length);
            if (item.labels.length === 0) {
              dropped++;
              return false;
            }
            return true;
          });
          fs.writeFileSync(outputPath, JSON.stringify(doc));
          core.info(`Sanitized label ops: removed=${removed}, dropped_messages=${dropped}`);
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# PR Labeler

Evaluate the pull request and apply one or more labels from the configured classification set.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} - ${{ github.event.pull_request.title }}
- **Allowed classification labels**: `${{ inputs.classification-labels }}`

## Goal

Apply classification labels that best represent the PR's risk or routing category.

## Instructions

1. Read the full PR details and changed files for #${{ github.event.pull_request.number }}.
1. Parse `${{ inputs.classification-labels }}` as a comma-separated list and treat that list as the only valid classification labels.
1. Select one or more labels from that parsed list and apply them with `add_labels`.
1. `add_labels` appends labels and does not remove existing ones.
1. If your classification scheme is mutually exclusive or you are replacing prior labels, remove outdated/conflicting labels first with `remove_labels`, then add the desired labels with `add_labels`.
1. When replacing/removing an existing classification label, use a high-confidence bar: if you are on the fence between keeping the current label vs switching it, keep the current label and avoid churn.
1. Never add or remove labels that are not in the parsed classification label list.
1. Use `${{ inputs.additional-instructions }}` to define label semantics and risk criteria for your selected label set.
1. If the PR cannot be evaluated at all, call `noop`.

${{ inputs.additional-instructions }}
