---
description: "Simplify overcomplicated code with high-confidence refactors"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-pr.md
engine:
  id: copilot
  model: gpt-5.2-codex
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
  group: code-simplifier
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
safe-outputs:
  noop:
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Code Simplifier

Simplify overcomplicated code with high-confidence, behavior-preserving refactors.

## Context

- **Repository**: ${{ github.repository }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, create a pull request.
- **CANNOT**: Directly push to the repository — use `create_pull_request`.
- **Only one PR per run.**
- Only make changes that are **provably** behavior-preserving and low risk.
- Keep changes small and localized (prefer 1-2 files and minimal line churn).
- Avoid refactors that change public APIs, configs, or behavior (including logging/telemetry).
- Prefer simplifying control flow (early returns), removing dead code, and replacing custom code with obvious standard library equivalents.
- If no safe simplification is found, call `noop` with a brief reason.
- **Most runs should end with `noop`.** Only open a PR for simplifications that are obviously correct at a glance. If a reviewer would need to think hard about whether behavior is preserved, it's not simple enough.

## Step 1: Find candidates

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Use search and file reading to identify overcomplicated code:
   - deep nesting
   - redundant conditionals
   - duplicated logic
   - verbose helpers that can be simplified

## Step 2: Select a target

Pick one small area where the simplification is obvious and easy to validate. Prioritize code with existing tests or easy-to-run checks.

## Step 3: Implement

1. Make the smallest safe change that preserves behavior.
2. Determine required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config; run required commands relevant to the change and capture results. If required commands cannot be run, call `noop`.
3. Run the most relevant targeted tests. **Tests must pass.** If no tests cover the changed code, this is a strong signal to call `noop` — untested simplifications are high-risk.

## Step 4: Quality Gate — Prove Safety

Before creating the PR, verify:

- **Required commands pass**: You ran required repo commands (lint/build/test) and they succeeded. State which commands and their results.
- **Behavior is identical**: You can explain in one sentence why the output is unchanged for all inputs.
- **No hidden side effects**: The change doesn't alter error handling, logging, metrics, or concurrency behavior.
- **Reviewer would approve quickly**: A maintainer would glance at this and merge, not debate it.

If any of these checks fail, call `noop`. A simplification that might change behavior is not a simplification.

## Step 5: Create the PR

Call `create_pull_request` with a concise summary, a clear explanation of why the change is safe, and the exact commands run with their results.

${{ inputs.additional-instructions }}
