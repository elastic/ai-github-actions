---
description: "Add focused tests for under-tested code and clean up redundant tests"
imports:
  - gh-aw-fragments/elastic-tools.md
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
  group: test-improvement
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
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  noop:
timeout-minutes: 45
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Test Improvement Agent

Identify under-tested code paths, add focused tests, and remove or consolidate duplicate or useless tests when safe. Open a single PR with the improvements.

## Context

- **Repository**: ${{ github.repository }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, create a pull request.
- **CANNOT**: Push directly to the repository — use `create_pull_request`.
- **Only one PR per run.**
- No large refactors; prioritize targeted test additions or small cleanup of redundant tests.
- If the change set is large or unsafe, call `noop` with a brief reason.
- **Most runs should end with `noop`.** Only open a PR when the added tests are clearly valuable — they test real behavior, not trivial getters, and they would catch actual regressions.

## Step 1: Gather context

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Determine how to run tests:
   - Check README, CONTRIBUTING, DEVELOPING, Makefile, package.json, pyproject.toml, and similar files.
3. Identify coverage tooling (nyc, jest --coverage, pytest --cov, go test -cover, etc.).
   - If coverage is available and reasonably fast, run it to find low-coverage files.

## Step 2: Identify targets

- Prefer low-coverage or untested public APIs, error paths, or recent changes without tests.
- Look for redundant tests:
  - identical assertions or test bodies,
  - tests that only duplicate coverage from more comprehensive tests.
- Only remove or merge tests when a clearer, equivalent test remains.

## Step 3: Implement improvements

1. Add minimal, focused tests in existing test suites.
2. Keep production code changes minimal and only when needed to enable testing.
3. Consolidate or remove redundant tests if safe, keeping behavior coverage intact.

## Step 4: Verify

- Run the most relevant test command(s). **All tests — new and existing — must pass.** If the full suite is too heavy, run targeted tests.
- If tests or coverage cannot be run, call `noop`. Do not open a PR with untested test code.

## Step 5: Quality Gate — Test Value Check

Before creating the PR, evaluate each new test:

- **Does it test real behavior?** Tests for trivial getters, simple constructors, or obvious pass-through functions are not worth filing a PR for.
- **Would it catch a real regression?** If the tested code changed in a buggy way, would this test actually fail?
- **Is it maintainable?** Fragile tests that break on cosmetic changes (string formatting, log messages) add burden, not value.
- **Does it follow project conventions?** Match the existing test style, naming, and organization.

If the tests don't pass this bar, call `noop`. Low-value tests are worse than no tests — they create maintenance burden and false confidence.

## Step 6: Create the PR

1. Commit the changes locally.
2. Call `create_pull_request` with:
   - **Title**: concise summary of the test improvements
   - **Body**: summary, what behavior the tests cover and why it matters, tests run and their results, and any removed or merged tests
3. If no safe improvements are found, call `noop` with a brief reason.

${{ inputs.additional-instructions }}
