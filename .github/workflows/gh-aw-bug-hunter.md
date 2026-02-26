---
inlined-imports: true
name: "Bug Hunter"
description: "Find a reproducible, user-impacting bug and file a report issue"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/ensure-full-history.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/scheduled-audit.md
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
      title-prefix:
        description: "Title prefix for created issues (e.g. '[bug-hunter]')"
        type: string
        required: false
        default: "[bug-hunter]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: bug-hunter
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, labels, actions]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Find a single reproducible, user-impacting bug in the repository that can be covered by a minimal failing test.

**The bar is high: you must actually reproduce the bug before filing.** Most runs should end with `noop` — that means the codebase is healthy.

### Data Gathering

1. Review recent changes:
   - Run `git log --since="28 days ago" --stat` and identify candidates with user-facing impact.
   - Read the diffs and related files for each candidate.
2. Check for existing reports:
   - Search open and closed issues for similar symptoms or areas before filing a new issue.
   - Prioritize Bug Hunter reports by searching `repo:{owner}/{repo} is:issue (label:bug-hunter OR in:title "[bug-hunter]")`.
   - If a close match exists, do not file a new issue.
3. Reproduce locally — this step is **mandatory**, not optional:
   - Write a **new** minimal reproduction: a small script or test case that directly triggers the specific bug you identified through code analysis. Do **not** run the existing test suite (e.g. `make test`, `pytest`, `go test ./...`) — if you did not write the test, a failure is not your finding.
   - Capture the exact steps and output from your reproduction.
   - If you cannot write a concrete reproduction that fails due to the bug, do **not** file it. Call `noop` instead.

### What to Look For

- Logic errors: incorrect conditionals, off-by-one errors, wrong variable used, missing edge-case handling.
- Clear user impact: command failure, incorrect output, broken workflow, or misconfiguration.
- Deterministic reproduction (not flaky). You must trigger the bug yourself with code you wrote.
- Can be expressed as a minimal failing test (unit, CLI, or workflow compilation step).

### What to Skip

- Theoretical concerns without a reproduction — **no "this looks like it could break."**
- Code that "looks wrong" but works correctly in practice.
- Test suite failures from running existing tests — do not run `make test` or similar and report the output as a bug.
- Edge cases that require unusual or undocumented inputs.
- Issues that require large refactors or design changes.
- Behavior already tracked by an open issue.

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- You could not write a concrete reproduction that triggers the bug and observed the failure.
- Your only evidence is an existing test failure you did not cause — you ran `make test` or similar and a test failed.
- The bug is speculative — you inferred it from reading code but did not trigger it with code you wrote.
- A similar issue is already open.
- The impact is cosmetic or low-severity (e.g., a typo in a log message).

### Issue Format

**Issue title:** Short bug summary

**Issue body:**

> ## Impact
> [Who/what is affected, why it matters]
>
> ## Reproduction Steps
> 1. [Exact commands you ran, including the new test or script you wrote]
>
> ## Expected vs Actual
> **Expected:** ...
> **Actual:** ... [Include actual command output]
>
> ## Failing Test
> [The new test or script you wrote that reproduces the bug — include the full code]
>
> ## Evidence
> - [Commands/output you captured during reproduction, file references, or links]

### Labeling

- If the `bug-hunter` label exists (check with `github-get_label`), include it in the `create_issue` call; otherwise, rely on the `[bug-hunter]` title prefix only.

${{ inputs.additional-instructions }}
