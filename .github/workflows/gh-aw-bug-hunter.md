---
description: "Find a reproducible, user-impacting bug and file a report issue"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
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
  group: bug-hunter
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
  create-issue:
    max: 1
    title-prefix: "[bug-hunter] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
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
   - Run `git log --since="14 days ago" --stat` and identify candidates with user-facing impact.
   - Read the diffs and related files for each candidate.
2. Check for existing reports:
   - Search open and closed issues for similar symptoms or areas before filing a new issue.
   - Prioritize Bug Hunter reports by searching `repo:{owner}/{repo} is:issue (label:bug-hunter OR in:title "[bug-hunter]")`.
   - If a close match exists, do not file a new issue.
3. Reproduce locally — this step is **mandatory**, not optional:
   - Use the smallest relevant command from the docs or Makefile to trigger the behavior (for example `make compile` or `scripts/dogfood.sh`).
   - Capture the exact steps and output.
   - If you cannot reproduce the bug, do **not** file it. Call `noop` instead.

### What to Look For

- Clear user impact: command failure, incorrect output, broken workflow, or misconfiguration.
- Deterministic reproduction (not flaky). You must reproduce it at least once yourself.
- Can be expressed as a minimal failing test (unit, CLI, or workflow compilation step).

### What to Skip

- Theoretical concerns without a reproduction — **no "this looks like it could break."**
- Code that "looks wrong" but works correctly in practice.
- Edge cases that require unusual or undocumented inputs.
- Issues that require large refactors or design changes.
- Behavior already tracked by an open issue.

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- You could not reproduce the bug with a concrete command and observed output.
- The bug is speculative — you inferred it from reading code but did not trigger it.
- A similar issue is already open.
- The impact is cosmetic or low-severity (e.g., a typo in a log message).

### Issue Format

**Issue title:** Short bug summary

**Issue body:**

> ## Impact
> [Who/what is affected, why it matters]
>
> ## Reproduction Steps
> 1. [Exact commands you ran]
>
> ## Expected vs Actual
> **Expected:** ...
> **Actual:** ... [Include actual command output]
>
> ## Suggested Failing Test
> [File path + outline of test]
>
> ## Evidence
> - [Commands/output you captured during reproduction, file references, or links]

### Labeling

- If the `bug-hunter` label exists (check with `github-get_label`), include it in the `create_issue` call; otherwise, rely on the `[bug-hunter]` title prefix only.

${{ inputs.additional-instructions }}
