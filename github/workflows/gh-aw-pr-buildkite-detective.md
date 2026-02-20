---
description: "Analyze failed Buildkite PR checks and report findings"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment.md
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
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: pr-buildkite-detective-${{ github.event.workflow_run.id }}
  cancel-in-progress: false
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
mcp-servers:
  buildkite:
    url: "https://mcp.buildkite.com/mcp/readonly"
    headers:
      Authorization: "Bearer ${{ secrets.BUILDKITE_API_TOKEN }}"
network:
  allowed:
    - defaults
    - github
    - "mcp.buildkite.com"
strict: false
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# PR Buildkite Detective

Assist with failed Buildkite checks for pull requests in ${{ github.repository }}. Analyze Buildkite build logs, explain failures, and recommend fixes. This workflow is read-only.

## Context

- **Repository**: ${{ github.repository }}
- **Workflow Run ID**: ${{ github.event.workflow_run.id }}
- **Conclusion**: ${{ github.event.workflow_run.conclusion }}
- **Buildkite Organization**: ${{ inputs.buildkite-org }}

## Constraints

- **CAN**: Read files, search code, run tests and commands, query Buildkite via MCP, comment on PRs
- **CANNOT**: Push changes, merge PRs, or modify `.github/workflows/`

## Instructions

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Identify the PRs associated with the workflow run using `github.event.workflow_run.pull_requests`. If there are none, call `noop` with message "No pull request associated with workflow run; nothing to do" and stop.
3. For each PR, call `pull_request_read` with method `get` to capture the author, branches, and fork status.
4. Resolve the Buildkite pipeline:
   - If `inputs.buildkite-pipeline` is set, use it.
   - Otherwise call Buildkite MCP `list_pipelines` for organization `${{ inputs.buildkite-org }}` and select the pipeline matching `${{ github.event.repository.name }}` (or nearest match).
5. Locate the failed build for this workflow run:
   - Call Buildkite MCP `list_builds` for the resolved pipeline and match by commit SHA `${{ github.event.workflow_run.head_sha }}` first.
   - If no SHA match is found, try branch `${{ github.event.workflow_run.head_branch }}` and select the latest failed build.
6. Fetch failure evidence:
   - Call `get_build` for the selected build.
   - For each failed job, call `get_job_logs`, `search_logs` (`error|Error|ERROR|failed|Failed|FAILED|panic|exception`), and `tail_logs`.
   - Call `list_annotations` to capture warnings/errors attached to the build.

### Step 2: Analyze

- Identify the failing job/step and summarize the root cause.
- Propose a concrete, minimal fix or remediation plan.
- If logs are inconclusive, state what additional data is needed.

### Step 3: Respond

Call `add_comment` on the PR with:
- A concise summary of the failure and root cause
- The Buildkite build URL and failing job names
- The recommended fix or remediation plan
- Tests run and their results (if any)
- Any follow-up steps required

${{ inputs.additional-instructions }}
