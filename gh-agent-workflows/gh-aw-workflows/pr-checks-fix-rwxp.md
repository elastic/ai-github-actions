---
# Shared pr-checks-fix prompt — no `on:` field (imported by the pr-checks-fix shim)
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment.md
  - gh-aw-fragments/safe-output-push-to-pr.md
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
network:
  allowed:
    - defaults
    - github
---

# PR Checks Fixer

Assist with failed GitHub Actions checks for pull requests in ${{ github.repository }}. Analyze workflow run logs, explain failures, and optionally push fixes.

## Context

- **Repository**: ${{ github.repository }}
- **Workflow Run ID**: ${{ github.event.workflow_run.id }}
- **Conclusion**: ${{ github.event.workflow_run.conclusion }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, comment on PRs, push changes to same-repo PR branches
- **CANNOT**: Push to fork PR branches, merge PRs, or modify `.github/workflows/`

When pushing changes, the workspace already has the PR branch checked out. Make your changes, run tests, commit them locally, then use `push_to_pull_request_branch`.

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

### Step 2: Analyze and Fix

- Identify the failing job/step and summarize the root cause.
- If the fix is straightforward and safe, implement it locally, run tests, commit, and push to the PR branch.
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
