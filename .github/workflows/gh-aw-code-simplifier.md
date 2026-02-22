---
inlined-imports: true
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
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
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
      allowed-bot-users:
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      draft-prs:
        description: "Whether to create pull requests as drafts"
        type: boolean
        required: false
        default: true
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
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
strict: false
safe-outputs:
  noop:
timeout-minutes: 90
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

## Bar for merit

A simplification must clear at least one of these bars to be worth submitting:

1. **Style conformance** — the code is a clear outlier compared to the rest of the codebase (e.g., one function uses a verbose pattern that every other function avoids). The change brings it in line with the established style.
2. **Helper reuse** — an existing utility or helper function already does what the code is reimplementing. The change replaces the inline logic with a call to the existing helper.
3. **Significant clarity or DRY improvement** — the change meaningfully reduces complexity or duplication (e.g., collapses 10+ lines of tangled logic into 2–3 readable lines, or eliminates a non-trivial copy-paste pattern across multiple sites).

**Do not submit** micro-changes that swap one valid idiom for another (e.g., replacing a two-line map lookup + nil check with a one-line direct access, renaming variables for style, or reordering equivalent expressions). These changes take longer to review than they provide benefit. If the best candidate you found is a micro-change, call `noop`.

## Step 1: Find candidates

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Use search and file reading to identify overcomplicated code:
   - deep nesting
   - redundant conditionals
   - duplicated logic
   - verbose helpers that can be simplified
   - code that is a style outlier compared to the rest of the codebase
   - inline logic that reimplements an existing helper

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
