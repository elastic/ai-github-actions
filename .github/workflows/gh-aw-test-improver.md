---
inlined-imports: true
name: "Test Improver"
description: "Add focused tests for under-tested code and clean up redundant tests"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
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
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: test-improver
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
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Test Improver Agent

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
2. Determine required repo commands (lint/build/test) and how to run tests:
   - Check README, CONTRIBUTING, DEVELOPING, Makefile, CI config, package.json, pyproject.toml, and similar files.
3. Identify coverage tooling (nyc, jest --coverage, pytest --cov, go test -cover, etc.).
   - If coverage is available and reasonably fast, run it to find low-coverage files.

## Step 2: Identify targets

- Prefer low-coverage or untested public APIs, error paths, or recent changes without tests.
- **Trace to user-facing behavior.** For every candidate, answer: "What end-to-end user action would exercise this code path?" If you cannot describe a concrete user scenario (e.g., "a user configures X and then Y happens"), the target is too internal to justify a PR.
- Prefer code paths reachable from public entry points (CLI commands, API endpoints, config parsing, UI interactions) over deeply internal helpers.
- Look for redundant tests:
  - identical assertions or test bodies,
  - tests that only duplicate coverage from more comprehensive tests.
- Only remove or merge tests when a clearer, equivalent test remains.

## Step 3: Implement improvements

1. Add minimal, focused tests in existing test suites.
2. Keep production code changes minimal and only when needed to enable testing.
3. Consolidate or remove redundant tests if safe, keeping behavior coverage intact.

## Step 4: Verify

- Run required repo commands (lint/build/test) relevant to the change and capture results.
- Run the most relevant test command(s). **All tests — new and existing — must pass.** If the full suite is too heavy, run targeted tests.
- If required commands, tests, or coverage cannot be run, call `noop`. Do not open a PR with untested test code.

## Step 5: Stability check — run new tests repeatedly

New tests that pass once may still be flaky. Before filing a PR, verify stability by running each new or modified test multiple times.

1. Run each new or modified test **at least 5 times** in sequence and confirm every run passes.
   - Use the test framework's built-in repeat/count flag when available (e.g., `go test -count=5`, `pytest -x --count 5` with `pytest-repeat`, `--repeat 5` in Jest/Vitest).
   - If no built-in mechanism exists, use a simple shell loop: `for i in $(seq 1 5); do <test-command> || exit 1; done`
2. If any run fails intermittently, investigate the root cause before proceeding. Common sources of flakiness:
   - Reliance on timing, sleep, or wall-clock assertions
   - Shared mutable state between test cases
   - Non-deterministic iteration order (e.g., map/set ordering)
   - Dependence on external services or network
3. If the test cannot be made reliably stable, do not include it in the PR. Call `noop` if no stable tests remain.

## Step 6: Quality Gate — Test Value Check

Before creating the PR, evaluate each new test:

- **Does it test real behavior?** Tests for trivial getters, simple constructors, or obvious pass-through functions are not worth filing a PR for.
- **Would it catch a real regression?** If the tested code changed in a buggy way, would this test actually fail?
- **Can you describe the user scenario?** For each test, you must be able to state: "A user doing [action] would hit this code path when [condition]." If you cannot connect the test to a describable end-to-end user experience, drop it.
- **Is it maintainable?** Fragile tests that break on cosmetic changes (string formatting, log messages) add burden, not value.
- **Does it follow project conventions?** Match the existing test style, naming, and organization.

If the tests don't pass this bar, call `noop`. Low-value tests are worse than no tests — they create maintenance burden and false confidence.

## Step 7: Create the PR

1. Commit the changes locally.
2. Call `create_pull_request` with:
   - **Title**: concise summary of the test improvements
   - **Body** must include:
     - Summary of what changed
     - **User scenario**: for each test, describe the real-world user action or workflow that exercises the tested code path (e.g., "When a user runs `beat setup` with an invalid config, this error path is triggered")
     - Why the tests matter — what regressions they would catch
     - Tests run and their results
     - Any removed or merged tests
3. If no safe improvements are found, call `noop` with a brief reason.

${{ inputs.additional-instructions }}
