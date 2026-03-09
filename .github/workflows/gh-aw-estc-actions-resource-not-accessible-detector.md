---
inlined-imports: true
description: "Daily detector for 'Resource not accessible by integration' across long-term branches"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
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
      look-back-days:
        description: "Number of days to look back when scanning failed workflow runs"
        type: number
        required: false
        default: 1
      title-prefix:
        description: "Title prefix for created issue (e.g. '[resource-not-accessible-by-integration]')"
        type: string
        required: false
        default: "[resource-not-accessible-by-integration]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-estc-actions-resource-not-accessible-detector
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
  - name: Prescan failed runs for target error
    env:
      GH_TOKEN: ${{ github.token }}
      LOOK_BACK_DAYS: ${{ inputs.look-back-days }}
      LONG_TERM_BRANCHES: ${{ inputs.long-term-branches }}
      DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
    run: |
      set -euo pipefail
      mkdir -p /tmp/gh-aw/agent

      since="$(date -u -d "${LOOK_BACK_DAYS} days ago" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-"${LOOK_BACK_DAYS}"d '+%Y-%m-%dT%H:%M:%SZ')"
      findings_file="/tmp/gh-aw/agent/resource-not-accessible-findings.tsv"
      printf "workflow_path\tbranch\trun_id\trun_url\tcreated_at\tevidence\n" > "$findings_file"

      branches=()
      for branch in "$DEFAULT_BRANCH" $LONG_TERM_BRANCHES; do
        [ -n "$branch" ] || continue
        skip=false
        for existing in "${branches[@]:-}"; do
          if [ "$existing" = "$branch" ]; then
            skip=true
            break
          fi
        done
        if [ "$skip" = false ]; then
          branches+=("$branch")
        fi
      done

      runs_file="/tmp/gh-aw/agent/resource-not-accessible-runs.tsv"
      : > "$runs_file"
      for branch in "${branches[@]}"; do
        gh api "repos/$GITHUB_REPOSITORY/actions/runs" \
          --method GET \
          -f branch="$branch" \
          -f status=failure \
          -f created=">=${since}" \
          --paginate \
          --jq '.workflow_runs[] | [.id, .html_url, .path, .head_branch, .created_at] | @tsv' \
          >> "$runs_file" || true
      done

      while IFS=$'\t' read -r run_id run_url workflow_path head_branch created_at; do
        [ -n "${run_id:-}" ] || continue
        zip_file="/tmp/gh-aw/agent/workflow-logs-${run_id}.zip"
        log_dir="/tmp/gh-aw/agent/workflow-logs-${run_id}"

        if ! gh api "repos/$GITHUB_REPOSITORY/actions/runs/${run_id}/logs" -H "Accept: application/vnd.github+json" > "$zip_file" 2>/dev/null; then
          continue
        fi
        rm -rf "$log_dir"
        if ! unzip -o "$zip_file" -d "$log_dir" >/dev/null 2>&1; then
          continue
        fi

        match="$(grep -R -n -m 3 "Resource not accessible by integration" "$log_dir" 2>/dev/null || true)"
        if [ -n "$match" ]; then
          evidence="${match//$'\t'/ }"
          evidence="${evidence//$'\n'/ | }"
          printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$workflow_path" "$head_branch" "$run_id" "$run_url" "$created_at" "$evidence" >> "$findings_file"
        fi
        rm -rf "$log_dir" "$zip_file"
      done < "$runs_file"

      matches="$(tail -n +2 "$findings_file" | wc -l | tr -d ' ')"
      workflows="$(tail -n +2 "$findings_file" | cut -f1 | sort -u | wc -l | tr -d ' ')"
      {
        echo "since=${since}"
        echo "look_back_days=${LOOK_BACK_DAYS}"
        echo "matched_runs=${matches}"
        echo "matched_workflows=${workflows}"
        echo "findings_file=${findings_file}"
      } > /tmp/gh-aw/agent/resource-not-accessible-summary.txt
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# Resource Not Accessible By Integration Detector

Use the prescan output to investigate only workflows that already matched `Resource not accessible by integration`, then create a single tracking issue with the combined analysis.

## Context

- **Repository**: ${{ github.repository }}
- **Default Branch**: ${{ github.event.repository.default_branch }}
- **Additional long-term branches**: ${{ inputs.long-term-branches }}
- **Look-back days**: ${{ inputs.look-back-days }}
- **Error pattern**: `Resource not accessible by integration`
- **Prescan summary**: `/tmp/gh-aw/agent/resource-not-accessible-summary.txt`
- **Prescan findings**: `/tmp/gh-aw/agent/resource-not-accessible-findings.tsv`
## Constraints

- **CAN**: Read files, search code, run commands, create one issue.
- **CANNOT**: Push changes or open PRs in this workflow.
- Only investigate workflows listed in `/tmp/gh-aw/agent/resource-not-accessible-findings.tsv`.
- Do not file a duplicate issue if an open `${{ inputs.title-prefix }}` issue already tracks the same workflows and failure pattern.

## Permission reference

`Resource not accessible by integration` means the `GITHUB_TOKEN` lacks a required scope. Common causes:

| Failed operation | Required permission |
| --- | --- |
| Create/update issues | `issues: write` |
| Create/update pull requests | `pull-requests: write` |
| Push code or tags | `contents: write` |
| Create releases | `contents: write` |
| Publish packages | `packages: write` |
| Trigger other workflows | `actions: write` |
| Manage deployments | `deployments: write` |
| Create/update checks | `checks: write` |
| Comment on PRs | `pull-requests: write` |

Common root causes:
- **Missing `permissions:` block** — the workflow relies on the repo/org default token permissions which are too restrictive.
- **Fork PRs** — `pull_request` from forks always gets a read-only token. Use `pull_request_target` (with caution) or a GitHub App token.
- **Organization policies** — org-level settings may cap the maximum token permissions.

The fix is to add an explicit `permissions:` block at the workflow or job level granting only the minimum required scopes. For each affected workflow, read its source file under `.github/workflows/`, identify the operation that failed from the evidence, and recommend the specific permission to add.

## Step 1: Gather context

1. Read `/tmp/gh-aw/agent/resource-not-accessible-summary.txt`.
2. Read `/tmp/gh-aw/agent/resource-not-accessible-findings.tsv`.

## Step 2: Decide whether to noop

- If the findings file has no data rows, call `noop` with:
  `No 'Resource not accessible by integration' failures found in the configured look-back window — nothing to report`.
- Check open issues for `${{ inputs.title-prefix }}` in the title and compare workflow paths/evidence.
- If an existing open issue already tracks the same findings, call `noop` and reference the existing issue number.

## Step 3: Investigate each affected workflow

For each workflow in the findings file:
1. Read the workflow source file from `.github/workflows/`.
2. Identify which operation failed from the evidence lines.
3. Check if the workflow already has a `permissions:` block and what scopes are granted.
4. Determine the minimum permission fix needed.

## Step 4: Produce combined analysis issue

Call `create_issue` exactly once with:

- **Title**: A short descriptive title summarizing the affected workflows (do NOT repeat the title-prefix in the title)
- **Body**:

  ````
  ## Scan Summary

  - Look-back days: <value from summary file>
  - Since: <value from summary file>
  - Matched workflows: <count>
  - Matched runs: <count>

  ## Affected Workflows

  | Workflow file | Branches | Runs |
  | --- | --- | --- |
  | <workflow path> | <comma-separated branches> | [<run-id>](<run_url>), ... |

  ## Evidence

  For each workflow include one or more verbatim evidence lines from the findings file.

  ## Root Cause Assessment

  For each workflow, explain which operation failed and why the current permissions are insufficient.

  ## Remediation

  For each workflow, provide the exact `permissions:` block to add or modify. Use before/after YAML snippets. Grant only the minimum required scopes.

  ## Next Steps

  - Apply the permission fixes manually under `.github/workflows/`.
  ````

${{ inputs.additional-instructions }}

