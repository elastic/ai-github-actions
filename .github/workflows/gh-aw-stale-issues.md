---
description: "Find open issues that appear to already be resolved and recommend closing them"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: gpt-5.2-codex
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
  group: stale-issues
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
network:
  allowed:
    - defaults
    - github
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  noop:
  create-issue:
    max: 1
    title-prefix: "[stale-issues] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Find open issues that are very likely already resolved and recommend them for closure. You do NOT close issues yourself — you file a report listing candidates with evidence.

### Data Gathering

1. **Get open issues**

   Search for open issues in the repository, starting with the oldest:
   ```
   github-search_issues: query="repo:{owner}/{repo} is:issue is:open sort:created-asc"
   ```

   Paginate through all open issues (use `per_page: 20`). For each issue, gather:
   - The issue title, body, and labels
   - The full comment thread via `issue_read` with method `get_comments`
   - Any linked PRs mentioned in comments or the issue body

2. **Check for resolving PRs**

   For each open issue, look for merged PRs that resolve it:
   - Search for PRs that reference the issue number: `repo:{owner}/{repo} is:pr is:merged {issue_number}`
   - Check if any merged PR body contains `fixes #{number}`, `closes #{number}`, or `resolves #{number}` (these may not have auto-closed the issue due to branch targeting or other reasons)
   - Check the issue timeline for linked PR events

3. **Check the codebase**

   For issues reporting bugs or requesting specific changes:
   - Read the relevant code to determine if the described problem still exists
   - Run tests if applicable to verify the fix
   - Check git log for commits that reference the issue number

### What Qualifies as "Very Likely Resolved"

Only flag an issue if you have **strong evidence** from at least one of these categories:

1. **Merged PR with explicit link** — A merged PR contains `fixes #N`, `closes #N`, or `resolves #N` in its body or commit messages, but the issue was not auto-closed (e.g., PR targeted a non-default branch)
2. **Code evidence** — The specific bug, missing feature, or requested change described in the issue is verifiably addressed in the current codebase. You must confirm this by reading the relevant code.
3. **Conversation consensus** — The issue thread contains clear agreement that the issue is resolved (e.g., the reporter confirmed the fix, a maintainer said "this is done"), but nobody closed it

### What to Skip

- Issues with recent activity (comments in the last 14 days) — someone is still working on them
- Issues labeled `epic`, `tracking`, `umbrella`, or similar meta-labels — these are intentionally kept open
- Issues where the resolution is ambiguous or you aren't sure
- Feature requests where you can't definitively confirm implementation
- Issues with open/unmerged PRs linked — work may still be in progress

**When in doubt, skip the issue.** False positives waste maintainer time and erode trust in the report. Only include issues where you are highly confident they are resolved.

### Issue Format

**Issue title:** Stale issues report — [count] issues likely resolved

**Issue body:**

> ## Resolved Issues Report
>
> The following open issues appear to already be resolved based on merged PRs, code evidence, or conversation consensus. Each entry includes the evidence supporting closure.
>
> ### 1. #[number] — [issue title]
>
> **Evidence:** [What makes you confident this is resolved]
> **Resolving PR:** #[PR number] (if applicable)
> **Recommendation:** Close as completed
>
> ### 2. #[number] — [issue title]
> ...
>
> ## Suggested Actions
>
> - [ ] Review and close #[number] — [one-line reason]
> - [ ] Review and close #[number] — [one-line reason]

**Guidelines:**
- Do not actually place the issue body in a block quote.
- Order by confidence level (most confident first)
- Always include the specific evidence — don't just say "this looks resolved"
- Link to the resolving PR, commit, or code when possible
- If no issues qualify, call `noop` with message "No stale issues found — all open issues appear to still be active or unresolved"

${{ inputs.additional-instructions }}
