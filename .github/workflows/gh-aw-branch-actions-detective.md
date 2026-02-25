---
inlined-imports: true
name: "Branch Actions Detective"
description: "Analyze failed branch CI runs and create or update a tracking issue"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
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
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: branch-actions-detective-${{ github.event.workflow_run.id }}
  cancel-in-progress: false
permissions:
  actions: read
  contents: read
  issues: read
tools:
  github:
    toolsets: [repos, issues, search, actions]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "[branch-actions-detective] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Branch Actions Detective

Analyze failed GitHub Actions CI runs on protected branches (e.g. `main`) in ${{ github.repository }}. Identify the root cause, assess impact, and create or update a tracking issue.

## Context

- **Repository**: ${{ github.repository }}
- **Workflow Run ID**: ${{ github.event.workflow_run.id }}
- **Conclusion**: ${{ github.event.workflow_run.conclusion }}
- **Default Branch**: ${{ github.event.repository.default_branch }}

## Constraints

- **CAN**: Read files, search code, run commands, read issues, create issues
- **CANNOT**: Push changes, merge PRs, or modify `.github/workflows/`

## Instructions

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Fetch workflow run details and logs with `bash` + `gh api`:
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
3. Check for existing open issues with the `[branch-actions-detective]` title prefix to avoid duplicates:
   ````bash
   gh api 'repos/{owner}/{repo}/issues?state=open&per_page=10' \
     --jq '.[] | select(.title | startswith("[branch-actions-detective]")) | {number: .number, title: .title, html_url: .html_url}'
   ````

### Step 2: Analyze

- Identify the failing job/step and summarize the root cause.
- Determine whether this is a new failure or a recurrence of an already-tracked issue.
- Assess impact: does this block merges, deployments, or other workflows?
- Propose a concrete, minimal fix or remediation plan.
- If the logs are inconclusive, state what additional data is needed.

### Step 3: Respond

**If an existing open `[branch-actions-detective]` issue tracks the same root cause:**
Call `noop` with a message explaining that the failure is already tracked by the existing issue (include the issue number).

**If this is a new or distinct failure:**
Call `create_issue` with the following format:

**Issue title:** Brief summary of the CI failure

**Issue body:**

> ## CI Failure Summary
>
> **Workflow:** [workflow name]
> **Branch:** [branch name]
> **Run:** [link to the failed run]
>
> ## Root Cause
>
> [Concise explanation of what failed and why]
>
> ## Impact
>
> [What is blocked or affected by this failure]
>
> ## Suggested Fix
>
> [Concrete steps or code changes to resolve the failure]
>
> ## Evidence
>
> - [Relevant log excerpts, file references, or links]

${{ inputs.additional-instructions }}
