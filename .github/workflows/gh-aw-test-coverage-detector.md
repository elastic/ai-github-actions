---
inlined-imports: true
name: "Test Coverage Detector"
description: "Find under-tested code paths and file a test coverage report"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/pick-three-keep-one.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/network-ecosystems.md
  - gh-aw-fragments/code-quality-audit.md
engine:
  id: copilot
  model: ${{ inputs.model }}
on:
  stale-check: false
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
        description: "Allowed bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      severity-threshold:
        description: "Minimum severity to include in the report. 'high' = only untested critical paths (error handling, auth, data mutations). 'medium' (default) = also include untested public APIs and recent changes. 'low' = also include minor coverage gaps."
        type: string
        required: false
        default: "medium"
      title-prefix:
        description: "Title prefix for created issues (e.g. '[test-coverage]')"
        type: string
        required: false
        default: "[test-coverage]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-test-coverage-detector
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
    close-older-key: "${{ inputs.title-prefix }}"
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Validate severity threshold
    env:
      SEVERITY_THRESHOLD: ${{ inputs.severity-threshold }}
    run: |
      case "$SEVERITY_THRESHOLD" in
        high|medium|low) ;;
        *)
          echo "Invalid severity-threshold: '$SEVERITY_THRESHOLD'. Expected one of: high, medium, low."
          exit 1
          ;;
      esac
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

Identify under-tested code paths that would benefit from focused tests and file a report issue with specific, actionable recommendations.

**The bar is high: you must identify concrete, high-value test gaps before filing.** Most runs should end with `noop` — that means test coverage is adequate.

### Severity Policy

Apply `${{ inputs.severity-threshold }}` using this explicit policy:
- `high` — include only untested critical paths (error handling, authentication/authorization, data mutations, and correctness-critical business logic).
- `medium` — include everything in `high`, plus untested public APIs and recent changes that lack tests.
- `low` — include everything in `medium`, plus minor but concrete coverage gaps that still map to a real user scenario.

### Data Gathering

1. Determine required repo commands (lint/build/test) and how to run tests:
   - Check README, CONTRIBUTING, DEVELOPING, Makefile, CI config, package.json, pyproject.toml, and similar files.
2. Identify coverage tooling (nyc, jest --coverage, pytest --cov, go test -cover, etc.).
   - If coverage is available and reasonably fast, run it to find low-coverage files.
   - If coverage tooling is not available, use code analysis to identify untested code paths.
3. Review recent changes:
   - Run `git log --since="28 days ago" --stat` and identify recent changes without corresponding test updates.
4. Use the **Pick Three, Keep One** pattern for the investigation phase: spawn 3 `general-purpose` sub-agents, each searching for test gaps from a different angle (e.g., one analyzing coverage reports, one reviewing recent commits for missing tests, one examining error paths and edge cases in public APIs). Include the repo conventions, coverage data, and the full "What to Look For" / "What to Skip" criteria in each sub-agent prompt. Each sub-agent should return its best candidate finding or recommend `noop`.

### What to Look For

- **Untested public APIs**: exported functions, CLI commands, API endpoints, or config parsing that have no or minimal test coverage.
- **Error paths**: exception handling, validation failures, and edge cases that are not exercised by any test.
- **Recent changes without tests**: code modified in the last 28 days where no corresponding test was added or updated.
- **Critical business logic**: core algorithms, data transformations, or state machines with insufficient coverage.
- **Trace to user-facing behavior.** For every candidate, answer: "What end-to-end user action would exercise this code path?" Only report gaps that map to a concrete user scenario.

### What to Skip

- Trivial getters, setters, or simple constructors — testing these adds maintenance burden without catching regressions.
- Generated code, vendored dependencies, or third-party code.
- Test files themselves.
- Code paths that are adequately covered by integration or end-to-end tests, even if unit coverage is low.
- Internal helper functions that are only reachable through already-tested public APIs.
- Subjective "should have more tests" observations without a concrete user scenario.

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- Coverage tooling shows adequate coverage and no clear gaps in critical paths.
- The only gaps found are trivial (getters, constructors, simple pass-through functions).
- You cannot describe a concrete user scenario for any identified gap.
- All gaps are already tracked in open issues.
- The codebase has no testable code (e.g., pure configuration, documentation-only).

### Issue Format

**Issue title:** Test coverage gaps (date)

**Issue body:**

> ## Summary
> - Coverage method: [tool used or manual analysis]
> - Files analyzed: [count]
> - Gaps identified: [count]
>
> ## Findings
>
> ### 1. [Brief description of the gap]
> **File:** `path/to/file.ext`
> **Function/Method:** `FuncName(...)`
> **User scenario:** [Describe the real-world user action that exercises this code path]
> **Why it matters:** [What regression could this catch? What could break?]
> **Suggested test approach:** [Brief description of what a test should verify]
>
> ## Suggested Actions
> - [ ] [Concrete action for each finding, e.g., "Add unit test for error handling in `ParseConfig` when config file is missing"]

### Labeling

- If the `test-coverage` label exists (check with `github-get_label`), include it in the `create_issue` call; otherwise, rely on the `${{ inputs.title-prefix }}` title prefix only.

${{ inputs.additional-instructions }}
