---
inlined-imports: true
description: "Analyze failed Buildkite PR checks and report findings"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
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
      target-pr-number:
        description: "Explicit PR number to target (used for manual/dispatch triggers)"
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
      buildkite-org:
        description: "Buildkite organization slug"
        type: string
        required: false
        default: "elastic"
      buildkite-pipeline:
        description: "Buildkite pipeline slug (optional; auto-discovered from repository if empty)"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      BUILDKITE_API_TOKEN:
        required: false
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
mcp-servers:
  buildkite:
    url: "https://mcp.buildkite.com/mcp/readonly"
    headers:
      Authorization: "Bearer ${{ secrets.BUILDKITE_API_TOKEN }}"
network:
  allowed:
    - "mcp.buildkite.com"
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
      echo "BK_EVENT_NAME=$GITHUB_EVENT_NAME" >> "$GITHUB_ENV"
      if [ "$GITHUB_EVENT_NAME" = "status" ]; then
        echo "BK_EVENT_ID=$(jq -r '.id' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_FAILURE_STATE=$(jq -r '.state' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_COMMIT_SHA=$(jq -r '.sha' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_TARGET_URL=$(jq -r '.target_url // empty' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_BRANCHES=$(jq -c '[.branches[].name]' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_PR_NUMBERS=" >> "$GITHUB_ENV"
      else
        echo "BK_EVENT_ID=$(jq -r '.check_run.id' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_FAILURE_STATE=$(jq -r '.check_run.conclusion' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_COMMIT_SHA=$(jq -r '.check_run.head_sha' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_TARGET_URL=$(jq -r '.check_run.details_url // empty' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
        echo "BK_BRANCHES=" >> "$GITHUB_ENV"
        echo "BK_PR_NUMBERS=$(jq -c '[.check_run.pull_requests[].number]' "$GITHUB_EVENT_PATH")" >> "$GITHUB_ENV"
      fi
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# PR Buildkite Detective

Analyze failed Buildkite CI builds for pull requests in ${{ github.repository }}. Identify root causes from build logs, trace failures to source code, and provide actionable fix recommendations via PR comments. This workflow is read-only.

## Context

- **Repository**: ${{ github.repository }}
- **Event Name**: ${{ env.BK_EVENT_NAME }}
- **Event ID**: ${{ env.BK_EVENT_ID }}
- **Failure State**: ${{ env.BK_FAILURE_STATE }}
- **Commit SHA**: ${{ env.BK_COMMIT_SHA }}
- **Target URL**: ${{ env.BK_TARGET_URL }}
- **PR Numbers**: ${{ env.BK_PR_NUMBERS }}
- **Branches**: ${{ env.BK_BRANCHES }}
- **Buildkite Organization**: ${{ inputs.buildkite-org }}

## Constraints

- **CAN**: Read files, search code, run tests and commands, query Buildkite via MCP, comment on PRs
- **CANNOT**: Push changes, merge PRs, or modify `.github/workflows/`

## Investigation Tools

Use the right tool for each task:

- **Buildkite MCP** (`list_pipelines`, `list_builds`, `get_build`, `get_job_logs`, `search_logs`, `tail_logs`, `list_annotations`): Query build information, job logs, and annotations
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

1. Use the commit SHA provided in the Context section above. If it is empty, discover it from the PR's commit statuses or check runs.
2. Find the associated pull request(s):
   - If **PR Numbers** in the Context section above is non-empty (e.g., from `check_run` events), use those PR numbers directly with `pull_request_read` method `get`.
   - Otherwise, use `bash` + `gh api repos/${{ github.repository }}/commits/{commit_sha}/pulls` to find PRs containing the commit SHA. If no results, also try searching open PRs whose head branch matches one of the **Branches** listed in the Context section.
   - If no PR is found after all attempts, call `noop` with message "No pull request associated with failed commit status; nothing to do" and stop.
3. For each matching PR, call `pull_request_read` with method `get` to capture the author, branches, and fork status for downstream analysis.

### Step 2: Find the Buildkite Build

> **If Buildkite MCP is unavailable** (connection error, 401, timeout, or empty token): Proceed with the **public pipeline** fallback described in Step 2b. Public Buildkite pipelines expose build pages and logs without authentication.

#### Step 2a: Via Buildkite MCP (when API token is available)

1. **Resolve the pipeline**: If `${{ inputs.buildkite-pipeline }}` is provided, use it. Otherwise, call `list_pipelines` for organization `${{ inputs.buildkite-org }}` and find the pipeline whose slug matches the repository name (extract the repo name from `${{ github.repository }}`). If multiple pipelines match, prefer an exact slug match.
2. **Find the failed build**: Call `list_builds` for the resolved pipeline, filtering by the failed commit SHA resolved in Step 1. If no match by SHA, use the PR's head branch (from the `pull_request_read` response in Step 1) to filter builds and select the most recent failed one.
3. **Collect failure evidence**:
   - Call `get_build` for the matched build to get overall status and job list.
   - For each **failed** job:
     - `get_job_logs` — retrieve the full log
     - `search_logs` with patterns: `error|Error|ERROR`, `failed|Failed|FAILED`, `panic|exception|traceback`
     - `tail_logs` — get the last 100 lines (often contains the final error and exit code)
   - Call `list_annotations` to capture any warnings, errors, or context the pipeline attached to the build.

#### Step 2b: Via public Buildkite pages (fallback when no API token)

Use this path when the Buildkite MCP server is unavailable (missing token, 401, connection error).

1. **Discover the Buildkite build URL** from the PR's commit statuses or check runs:
   - Call `pull_request_read` with method `get_status` for the PR to retrieve commit status contexts.
   - Look for status contexts or check runs whose `target_url` contains `buildkite.com`. The URL typically follows the pattern `https://buildkite.com/<org>/<pipeline>/builds/<number>`.

1. **Fetch the public build page**: Use `web-fetch` to retrieve the Buildkite build URL found above. The page contains the build status, job list, and links to individual job logs.

3. **Collect failure evidence from public pages**:
   - Parse the fetched build page to identify failed jobs. Look for job links matching the pattern `https://buildkite.com/<org>/<pipeline>/builds/<number>#<job-uuid>`.
   - For each failed job, use `web-fetch` to retrieve the job log page at `https://buildkite.com/<org>/<pipeline>/builds/<number>/jobs/<job-uuid>/log`.
   - Extract error messages, stack traces, and the final output from the fetched log content.
   - If the pipeline is not publicly accessible (403/404), note this in your comment and proceed with whatever evidence is available from GitHub status contexts.

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
