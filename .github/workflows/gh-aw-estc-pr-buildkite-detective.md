---
inlined-imports: true
description: "Analyze failed Buildkite PR checks and report findings"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-pr-hide-older.md
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
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      BUILDKITE_API_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
    - "buildkite-limited-access[bot]"
concurrency:
  group: ${{ github.workflow }}-estc-pr-buildkite-detective-${{ github.run_id }}
  cancel-in-progress: false
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
    - "buildkite.com"
safe-outputs:
  activation-comments: false
  noop:
strict: false
timeout-minutes: 30
steps:
  - name: Resolve event context
    run: |
      set -euo pipefail
      mkdir -p /tmp/gh-aw
      {
        echo "event_name: $GITHUB_EVENT_NAME"
        if [ "$GITHUB_EVENT_NAME" = "status" ]; then
          echo "event_id: $(jq -r '.id' "$GITHUB_EVENT_PATH")"
          echo "failure_state: $(jq -r '.state' "$GITHUB_EVENT_PATH")"
          echo "commit_sha: $(jq -r '.commit.sha' "$GITHUB_EVENT_PATH")"
          echo "target_url: $(jq -r '.target_url // empty' "$GITHUB_EVENT_PATH")"
          echo "branches: $(jq -r '[(.branches // [])[].name] | join(", ")' "$GITHUB_EVENT_PATH")"
          echo "pr_numbers:"
        else
          echo "event_id: $(jq -r '.check_run.id' "$GITHUB_EVENT_PATH")"
          echo "failure_state: $(jq -r '.check_run.conclusion' "$GITHUB_EVENT_PATH")"
          echo "commit_sha: $(jq -r '.check_run.head_sha' "$GITHUB_EVENT_PATH")"
          echo "target_url: $(jq -r '.check_run.details_url // empty' "$GITHUB_EVENT_PATH")"
          echo "branches:"
          echo "pr_numbers: $(jq -r '[(.check_run.pull_requests // [])[].number | tostring] | join(", ")' "$GITHUB_EVENT_PATH")"
        fi
      } > /tmp/gh-aw/buildkite-event.txt
      echo "Buildkite event context:"
      cat /tmp/gh-aw/buildkite-event.txt
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      BUILDKITE_API_TOKEN: ${{ secrets.BUILDKITE_API_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# PR Buildkite Detective

Analyze failed Buildkite CI builds for pull requests in ${{ github.repository }}. Identify root causes from build logs, trace failures to source code, and provide actionable fix recommendations via PR comments. This workflow is read-only.

## Context

- **Repository**: ${{ github.repository }}

**Read `/tmp/gh-aw/buildkite-event.txt` first.** It contains the event context (commit SHA, target URL, PR numbers, branches, failure state) extracted from the GitHub event payload.

## Constraints

- **CAN**: Read files, search code, run tests and commands, comment on PRs
- **CANNOT**: Push changes, merge PRs, or modify `.github/workflows/`

## Investigation Tools

Use the right tool for each task:

- **`search_code`**: Search code in *other* public GitHub repositories — use for finding upstream API changes, reference implementations, or migration guides. Use `grep` and file reading for the local codebase.
- **`web-fetch`**: Fetch documentation pages, changelogs, or API references for libraries and tools involved in the failure
- **`bash`**: Run tests locally to verify your analysis, reproduce failures, or check dependency versions

## Failure Categories

Classify each failure to guide your investigation:

- **Code bug**: Logic error, syntax error, type mismatch, nil/null dereference — trace to the specific source file and line
- **Test failure**: Assertion mismatch, test timeout, flaky test — check if the test itself is wrong or if the code under test changed
- **Dependency issue**: Missing package, version conflict, lockfile drift, network fetch failure — check dependency files and lockfiles
- **Infrastructure**: Resource exhaustion, service unavailability, timeout, Docker pull failure — often transient; recommend retry if so
- **Configuration**: Invalid settings, missing secrets/env vars, incorrect paths — check CI config, environment setup, and workflow definitions

## Instructions

### Step 1: Gather Context

1. Read `/tmp/gh-aw/buildkite-event.txt` to get the event context. Use the `commit_sha` value. If it is empty, discover it from the PR's commit statuses or check runs.
2. Find the associated pull request(s):
   - If `pr_numbers` is non-empty (from `check_run` events), use those PR numbers directly with `pull_request_read` method `get`.
   - Otherwise, use `bash` + `gh api repos/${{ github.repository }}/commits/{commit_sha}/pulls` to find PRs containing the commit SHA. Filter the results to keep only PRs whose `state` is `"open"` and, when `branches` is non-empty, whose `head.ref` matches one of the listed branches. If no candidates remain, also try searching open PRs whose head branch matches one of the branches.
   - If no PR is found after all attempts, call `noop` with message "No pull request associated with failed commit status; nothing to do" and stop.
3. For each matching PR, call `pull_request_read` with method `get` to capture the author, branches, and fork status for downstream analysis.

### Step 2: Read the Pre-Fetched Buildkite Data

Read `/tmp/gh-aw/buildkite-failures.txt` — it contains a summary of all failed Buildkite jobs for this PR, with the path to each job's log file. Then read the individual log files listed in the summary (under `/tmp/gh-aw/buildkite-logs/`) to get the full failure output.

If the file does not exist, call `noop` with message "No pre-fetched Buildkite failure data found; nothing to do" and stop.

### Step 3: Analyze

1. **Identify the failure**: Which job(s) and step(s) failed? What is the specific error message or stack trace?
2. **Trace to source code**: Use `grep` and file reading to find the relevant source files. Check recent changes in the PR diff that may have introduced the failure.
3. **Classify the failure**: Use the failure categories above to determine the type. This guides your fix recommendation.
4. **Research if needed**: If the error involves an external library, API, or tool, use `web-fetch` to check documentation or changelogs for known issues, breaking changes, or migration guides.
5. **Propose a fix**: Provide a concrete, minimal fix or remediation plan. If you can run tests locally to verify your theory, do so.
6. **Handle inconclusive cases**: If logs are insufficient to determine root cause, state exactly what additional data is needed and suggest next steps the author can take.

### Step 4: Respond

Call `add_comment` on the PR with the following structure:

**Build**: Link to the Buildkite build

**What failed**: Which job(s) and step(s) failed

**Error**: The key error message(s) or stack trace

**Root cause**: What caused the failure and why (with file paths and line numbers where applicable)

**Recommended fix**: Specific steps to resolve, with code snippets if applicable

**Verification**: Tests you ran locally (if any) and their results

Use `<details>` blocks for long log excerpts or stack traces to keep the comment scannable.

${{ inputs.additional-instructions }}
