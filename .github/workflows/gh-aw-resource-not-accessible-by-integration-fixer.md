---
inlined-imports: true
description: "Daily fixer for 'Resource not accessible by integration' across long-term branches"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-pr.md
  - gh-aw-fragments/workflow-edit-guardrails.md
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
      long-term-branches:
        description: "Space-separated list of long-term branch names to scan in addition to the default branch (e.g. 'main 8.x 7.17')"
        type: string
        required: false
        default: ""
      draft-prs:
        description: "Whether to create pull requests as drafts"
        type: boolean
        required: false
        default: false
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: resource-not-accessible-by-integration-fixer
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
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Resource Not Accessible By Integration Fixer

Scan workflow runs from the last 24 hours across all long-term branches in ${{ github.repository }}, find failures caused by `Resource not accessible by integration`, and open one remediation PR per affected workflow.

## Context

- **Repository**: ${{ github.repository }}
- **Default Branch**: ${{ github.event.repository.default_branch }}
- **Additional long-term branches**: ${{ inputs.long-term-branches }} (space-separated; empty means default branch only)
- **Error pattern**: `Resource not accessible by integration`
- **Remediation instructions URL**: `https://raw.githubusercontent.com/elastic/observability-cicd/main/github-actions/actionable/alerts/app/prompts/accessible-by-integration.txt`

## Constraints

- **CAN**: Read files, search code, modify files locally, run commands, create pull requests.
- **CANNOT**: Push directly to the repository — use `create_pull_request`. Merge or close PRs.
- **One PR per failing workflow** (never combine fixes for different workflows into a single PR).
- Scope: default branch plus all branches listed in `long-term-branches`.
- If no runs match the error pattern, call `noop` with message "No 'Resource not accessible by integration' failures found in the last 24 hours — nothing to fix".
- **Do not auto-merge.** Leave every PR open for review by the `elastic/observablt-ci` team.

## Step 1: Gather context

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Load the remediation instructions at runtime via `web_fetch`:
   ```
   https://raw.githubusercontent.com/elastic/observability-cicd/main/github-actions/actionable/alerts/app/prompts/accessible-by-integration.txt
   ```
   Store the content for use in Step 3. If the fetch fails, fall back to the general principle: add the minimum required `permissions` block to the failing workflow jobs or use a `GITHUB_TOKEN` with sufficient scopes.
3. Determine the scan window — the ISO 8601 timestamp for 24 hours ago:
   ````bash
   SINCE=$(date -u -d '24 hours ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null \
     || date -u -v-24H '+%Y-%m-%dT%H:%M:%SZ')
   echo "Scan since: $SINCE"
   ````
4. Build the branch list: always start with the repository default branch, then append the space-separated values from `${{ inputs.long-term-branches }}` (skip duplicates and blanks).

## Step 2: Scan for failures

For each branch in scope:

1. List failed workflow runs created since `$SINCE`:
   ````bash
   gh api "repos/${{ github.repository }}/actions/runs" \
     --method GET \
     -f branch=BRANCH_NAME \
     -f status=failure \
     -f created=">=${SINCE}" \
     --paginate \
     --jq '.workflow_runs[] | {id: .id, name: .name, html_url: .html_url, path: .path, head_branch: .head_branch, created_at: .created_at}'
   ````

2. For each failed run, download and search logs for the exact string `Resource not accessible by integration`:
   ````bash
   mkdir -p /tmp/gh-aw/agent
   gh api "repos/${{ github.repository }}/actions/runs/{run_id}/logs" \
     -H "Accept: application/vnd.github+json" \
     > /tmp/gh-aw/agent/workflow-logs-{run_id}.zip
   unzip -o /tmp/gh-aw/agent/workflow-logs-{run_id}.zip \
     -d /tmp/gh-aw/agent/workflow-logs-{run_id}/
   grep -rl "Resource not accessible by integration" \
     /tmp/gh-aw/agent/workflow-logs-{run_id}/ || true
   ````

3. Collect all runs where the log search returned matches. Group matching runs by the **workflow path** (the `.github/workflows/` file that defines the workflow) — this ensures exactly one PR per workflow, even when multiple runs or branches are affected.

If no runs match after scanning all branches, call `noop` with message "No 'Resource not accessible by integration' failures found in the last 24 hours — nothing to fix".

## Step 3: Analyze and fix each affected workflow

For each distinct workflow path that produced at least one matching run:

1. Read the workflow file from the repository:
   ````bash
   cat .github/workflows/<workflow-file>
   ````

2. Extract the exact log lines containing `Resource not accessible by integration` from a representative failing run as evidence (copy verbatim).

3. Apply the remediation instructions loaded in Step 1 as the primary fix policy. Follow those instructions exactly when patching the workflow file's permissions or token configuration.

4. Because workflow files live under `.github/workflows/`, follow the workflow-edit guardrails: place the patched copy in `github/workflows/` (without the leading dot). The PR body must note that a maintainer must rename the directory back to `.github/workflows/` before merging.

## Step 4: Quality gate

Before creating any PR:

- Confirm the patch resolves the permission issue described in the evidence.
- Confirm each change is minimal — only add or adjust the permissions or token configuration required to fix the error.
- Call `ready_to_make_pr`.

## Step 5: Create one PR per affected workflow

For each patched workflow, call `create_pull_request` with:

- **Title**: `fix(ci): resolve "Resource not accessible by integration" in <workflow-name> [<branch>]`
  - Include the branch only when the failure is branch-specific; omit it for failures across all branches.
- **Body** (all sections required):

  ```
  ## Affected Workflow

  - **File**: `.github/workflows/<workflow-file>`
  - **Workflow name**: <workflow-name>

  ## Failing Runs

  | Branch | Run | Created |
  | --- | --- | --- |
  | <branch> | [<run-id>](<html_url>) | <created_at> |

  ## Failure Evidence

  ```
  <verbatim log excerpt containing "Resource not accessible by integration">
  ```

  ## Root Cause

  <Concise explanation of why the permission was missing>

  ## Remediation Applied

  <Description of the change made, with reference to the external instructions URL>

  Source: https://raw.githubusercontent.com/elastic/observability-cicd/main/github-actions/actionable/alerts/app/prompts/accessible-by-integration.txt

  ## Reviewer Note

  This PR was created by an automated fixer. Please review and approve.
  The patched file is in `github/workflows/` — a maintainer must move it to `.github/workflows/` before merging.
  ```

- **Reviewers**: request review from team `elastic/observablt-ci`.

> **Important**: Do NOT merge the PR. Leave it open for review by `elastic/observablt-ci`.

${{ inputs.additional-instructions }}
