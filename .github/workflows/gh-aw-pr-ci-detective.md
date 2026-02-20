---
description: "Analyze failed PR checks and report findings"
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
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: pr-ci-detective-${{ github.event.workflow_run.id }}
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
    - defaults
    - github
strict: false
roles: [admin, maintainer, write]
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# PR CI Detective

Assist with failed GitHub Actions checks for pull requests in ${{ github.repository }}. Analyze workflow run logs, explain failures, and recommend fixes. This workflow is read-only.

## Context

- **Repository**: ${{ github.repository }}
- **Workflow Run ID**: ${{ github.event.workflow_run.id }}
- **Conclusion**: ${{ github.event.workflow_run.conclusion }}

## Constraints

- **CAN**: Read files, search code, run tests and commands, comment on PRs
- **CANNOT**: Push changes, merge PRs, or modify `.github/workflows/`

## Instructions

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Identify the PRs associated with the workflow run using `github.event.workflow_run.pull_requests`. If there are none, call `noop` with message "No pull request associated with workflow run; nothing to do" and stop.
3. For each PR, call `pull_request_read` with method `get` to capture the author, branches, and fork status.
4. Fetch workflow run details and logs with `bash` + `gh api`:
   - List jobs and their conclusions:
     ````bash
     gh api repos/{owner}/{repo}/actions/runs/{run_id}/jobs \
       --jq '.jobs[] | {id: .id, name: .name, conclusion: .conclusion, html_url: .html_url}'
     ````
   - Download logs to `/tmp/gh-aw/agent/` and inspect the failing step output:
     ````bash
     gh api repos/{owner}/{repo}/actions/runs/{run_id}/logs \
       -H "Accept: application/vnd.github+json" \
       > /tmp/gh-aw/agent/workflow-logs-{run_id}.zip
     unzip -o /tmp/gh-aw/agent/workflow-logs-{run_id}.zip -d /tmp/gh-aw/agent/workflow-logs-{run_id}/
     ````

### Step 2: Analyze

- Identify the failing job/step and summarize the root cause.
- Propose a concrete, minimal fix or remediation plan.
- If the logs are inconclusive, state what additional data is needed.

### Step 3: Respond

Call `add_comment` on the PR with:
- A concise summary of the failure and root cause
- The recommended fix or remediation plan
- Tests run and their results (if any)
- Any follow-up steps required

${{ inputs.additional-instructions }}
