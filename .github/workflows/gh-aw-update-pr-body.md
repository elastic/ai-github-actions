---
description: "Update PR body when code changes cause it to drift from the current state"
timeout-minutes: 60
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-update-pr.md
engine:
  id: copilot
  model: gpt-5.3-codex
  concurrency:
    group: "gh-aw-copilot-update-pr-body-${{ github.event.pull_request.number }}"
on:
  workflow_call:
    inputs:
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
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: update-pr-body-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
network:
  allowed:
    - defaults
    - github
    - go
    - node
    - python
    - ruby
strict: false
roles: [admin, maintainer, write]
bots:
  - "github-actions[bot]"
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# PR Body Update Agent

Keep the pull request body in sync with the actual state of the code changes in ${{ github.repository }}.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} — ${{ github.event.pull_request.title }}

## Objective

Determine whether the current PR body accurately reflects the code changes in this PR. If the body is significantly out of date or missing key information about the current diff, update it. Minor wording differences are not significant — only update when the body would meaningfully mislead a reviewer.

## Instructions

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Call `pull_request_read` with method `get` on PR #${{ github.event.pull_request.number }} to get the full PR details — current body, commits, and file list.
3. Call `pull_request_read` with method `get_files` to get the list of changed files.
4. If the PR description references issues (e.g., "Fixes #123", "Closes #456"), call `issue_read` with method `get` on each linked issue to understand the original motivation.

### Step 2: Analyze the Diff

Run `git log --oneline ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}` to see the commit history, then read the actual diff:

```bash
git diff --stat ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}
```

For key changed files, read relevant sections to understand the scope and nature of the changes.

### Step 3: Evaluate Drift

Compare the current PR body to what the diff actually contains. The body has **significant drift** if:

1. **Missing major features or changes** — a new public API, endpoint, configuration option, or workflow was added/removed/renamed that the body doesn't mention
2. **Incorrect description** — the body describes behavior that the code no longer implements, or describes files/functions that were subsequently renamed or removed
3. **Empty or placeholder body** — the PR body is blank, a template stub, or says something like "TODO" or "add description"
4. **Scope mismatch** — the body describes a narrow fix but the diff shows broad refactoring (or vice versa), leaving reviewers without an accurate picture

Do **not** update when:
- The body is a reasonable high-level summary even if some details differ
- Only minor wording could be improved
- The change is purely cosmetic or test-only and the body already captures the intent
- An update would erase useful context (motivation, design decisions, issue links) that the author provided

### Step 4: Update or Noop

**If there is significant drift:**

Call `update_pull_request` with a `replace` operation to write a body that:
- Preserves the original motivation and context (including issue links like `Fixes #N`)
- Accurately describes what was actually changed in the diff
- Follows the style and format conventions of the original body (if any)
- Is concise — one clear paragraph per major concern, no padding

**If the body is accurate enough:**

Call `noop` with a brief message like "PR body accurately reflects the current diff — no update needed."

${{ inputs.additional-instructions }}
