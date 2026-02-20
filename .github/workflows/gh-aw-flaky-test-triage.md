---
description: "Investigate flaky tests from issues and failed CI runs; file triage reports"
timeout-minutes: 60
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: gpt-5.3-codex
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
  group: flaky-test-triage
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
    title-prefix: "[flaky-test-triage] "
    close-older-issues: true
    expires: 7d
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

## Report Assignment

Detect flaky tests by combining open issues likely related to flakiness and recent failed CI runs, then file one evidence-based triage issue when concrete action is needed.

### Data Gathering

1. Discover candidate flakiness labels for this repository (for example labels containing `flaky`, `flakey`, or `intermittent`) and use them when searching issues.
2. Search open issues for likely flaky-test reports using discovered labels plus keyword fallback (`flaky`, `flakey`, `intermittent`), then gather:
   - failing test names
   - workflow/job names
   - links to logs or run IDs
3. Inspect failed workflow runs from the last 7 days:
   - Use `github` Actions APIs (or `gh api`) to list recent failed runs.
   - For candidate runs, list failed jobs and inspect logs in `/tmp/gh-aw/agent/`.
4. Build a frequency map of repeated failing tests across runs/issues.
5. Check for duplicates:
   - existing open flaky-triage issues
   - open PRs that already fix the same repeated failure

### What to Look For

- Failures that recur across multiple runs or branches.
- Same test failing with different surrounding stack traces or timing symptoms.
- Environment-sensitive failures (race, timeout, order dependence, resource contention).
- Existing retry/timeout mitigations that mask a persistent underlying defect.

### Analysis Rules

- Only recommend a fix when you have identified the **true root cause** with clear, supporting evidence — not a hypothesis. A noop is always preferable to a speculative or workaround fix.
- Retries, timeouts, and quarantine are **not fixes**. Do not recommend them as remediation steps. They may be noted as existing mitigations already in place, but never as the recommended action.
- Do not report one-off or non-reproducible failures lacking repeat evidence.
- Do not include items already tracked by a current open issue/PR unless new, material evidence changes prioritization.

### Quality Gate — When to Noop

Call `noop` when:
- no repeated flaky pattern is found, or
- all repeated failures are already actively tracked with sufficient detail, or
- a root cause cannot be clearly identified from the available evidence, or
- the only available remediation is a workaround (retry, timeout, quarantine) rather than a true fix.

### Issue Format

**Issue title:** Brief flaky-test triage summary for the window

**Issue body:**

> ## Flaky Test Triage Report
>
> **Window:** [date range analyzed]
>
> ### 1. [Test or failure cluster]
> **Evidence:**
> - Run(s): [links]
> - Job(s): [names]
> - Frequency: [count]
> - Representative error: [short snippet]
>
> **Root cause:** [specific, evidence-based — only include if truly identified; otherwise do not file an issue]
> **Recommended fix:** [concrete root-cause fix steps]
>
> ## Suggested Actions
> - [ ] [Concrete fix task]
> - [ ] [Validation task to confirm stability]

${{ inputs.additional-instructions }}
