---
inlined-imports: true
name: "Flaky Test Investigator"
description: "Investigate flaky tests from issues and failed CI runs; file triage reports"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
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
        description: "Title prefix for created issues (e.g. '[flaky-test-investigator]')"
        type: string
        required: false
        default: "[flaky-test-investigator]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-flaky-test-investigator
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

### Triage Reports (When Root Cause Is Unclear)

When a **clear repeated failure pattern** exists (3+ occurrences across different runs) but the root cause cannot be definitively identified from available CI logs alone, file a **triage report** instead of a full investigation. A triage report:

- Documents the failure pattern (test name, frequency, error signatures)
- Lists affected runs with links
- Provides candidate hypotheses ranked by likelihood based on available evidence
- Suggests concrete investigation steps a developer could take (e.g., "add timing instrumentation to X", "check if Y resource is shared across parallel jobs")
- Does NOT recommend retries, timeouts, or quarantine as solutions

Use the issue title format: `Flaky pattern: [test name] — triage needed`

### Quality Gate — When to Noop

Call `noop` when:
- no repeated flaky pattern is found (fewer than 3 occurrences), or
- all repeated failures are already actively tracked with sufficient detail, or
- the failure occurred only once and lacks repeat evidence.

### Issue Format

**Issue title:** Brief flaky-test investigation summary for the window

**Issue body:**

> ## Flaky Test Investigation Report
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
