---
inlined-imports: true
description: "Opt-in fixer for failed PR checks that can push safe, targeted changes"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-pr.md
  - gh-aw-fragments/safe-output-push-to-pr.md
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
      workflow-run-id:
        description: "Workflow run ID to analyze"
        type: string
        required: true
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
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-pr-actions-fixer-${{ inputs.workflow-run-id }}
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
safe-outputs:
  activation-comments: false
  max-patch-size: 10240
strict: false
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# PR Actions Fixer

Assist with failed GitHub Actions checks for pull requests in ${{ github.repository }}. This workflow is opt-in and uses a provided workflow run ID.

## Context

- **Repository**: ${{ github.repository }}
- **Workflow Run ID**: ${{ inputs.workflow-run-id }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, comment on PRs, push changes to same-repo PR branches
- **CANNOT**: Push to fork PR branches, merge PRs, or modify `.github/workflows/`

## Instructions

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Fetch workflow run details using `inputs.workflow-run-id`:
   ````bash
   gh api repos/${{ github.repository }}/actions/runs/{run_id} \
     --jq '{id: .id, html_url: .html_url, pull_requests: .pull_requests}'
   ````
3. Identify the PRs associated with the workflow run from the response. If there are none, call `noop` with message "No pull request associated with workflow run; nothing to do" and stop.
4. For each PR, call `pull_request_read` with method `get` to capture the author, branches, and fork status.
5. Fetch workflow run details and logs with `bash` + `gh api`:
   - List jobs and their conclusions:
     ````bash
     gh api repos/${{ github.repository }}/actions/runs/{run_id}/jobs \
       --jq '.jobs[] | {id: .id, name: .name, conclusion: .conclusion, html_url: .html_url}'
     ````
   - Download logs to `/tmp/gh-aw/agent/` and inspect the failing step output:
     ````bash
     gh api repos/${{ github.repository }}/actions/runs/{run_id}/logs \
       -H "Accept: application/vnd.github+json" \
       > /tmp/gh-aw/agent/workflow-logs-{run_id}.zip
     unzip -o /tmp/gh-aw/agent/workflow-logs-{run_id}.zip -d /tmp/gh-aw/agent/workflow-logs-{run_id}/
     ````

### Step 2: Analyze and Fix

- Identify the failing job/step and summarize the root cause.
- If the fix is straightforward and safe, implement it locally, run tests, and push to the PR branch.
- If the fix is risky or requires broader refactoring, propose a concrete remediation plan instead of pushing.
- If the PR is from a fork, do not push; provide patch guidance in the comment.

### Step 3: Respond

Call `add_comment` on the PR with:
- A concise summary of the failure and root cause
- The recommended fix (or the applied fix if you pushed changes)
- Tests run and their results
- Any follow-up steps required

**Additional tools:**
- `push_to_pull_request_branch` — push committed changes to the PR branch (same-repo PRs only)

${{ inputs.additional-instructions }}
