---
inlined-imports: true
name: "Stale Issues"
description: "Find open issues that appear to already be resolved and recommend closing them"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-audit.md
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
      close-older-issues:
        description: "Whether to close older issues with the same title prefix when a new one is created"
        type: boolean
        required: false
        default: true
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
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
    - go
    - node
    - python
    - ruby
strict: false
safe-outputs:
  noop:
  create-issue:
    max: 1
    title-prefix: "[stale-issues] "
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

Find open issues that are very likely already resolved and recommend them for closure. You do NOT close issues yourself — you file a report listing candidates with evidence.

### Data Gathering

1. **Build a candidate set (progressive age tiers)**

   Start with the oldest issues and work toward newer ones. Run high-signal queries first, then fill with dormant-issue queries tier by tier until you have at least 10 candidates or exhaust all tiers.


   **Dormant-issue tiers (oldest first):**
   ```
   Tier 1: updated:<{today - 90 days}
   Tier 2: updated:<{today - 60 days}
   Tier 3: updated:<{today - 30 days}
   ```

   Run Tier 1 first. If the total candidate pool (high-signal + dormant) has fewer than 10 issues after de-duplication, run Tier 2. If still under 10, run Tier 3. Stop as soon as you reach 10+ candidates or exhaust all tiers.

   Paginate each query (use `per_page: 50`), collect issue numbers, and de-duplicate across all queries.

2. **Fetch candidate details**

   For each candidate issue, gather:
   - The issue title, body, and labels
   - The full comment thread via `issue_read` with method `get_comments`
   - Any linked PRs mentioned in comments or the issue body

   Track coverage stats: total open issues (from `repo:{owner}/{repo} is:issue is:open`), candidate count, and fully analyzed count.

3. **Check for resolving PRs**

   For each candidate issue, look for merged PRs that resolve it:
   - Search for PRs that reference the issue number: `repo:{owner}/{repo} is:pr is:merged {issue_number}`
   - Check if any merged PR body contains `fixes #{number}`, `closes #{number}`, or `resolves #{number}` (these may not have auto-closed the issue due to branch targeting or other reasons)
   - Check the issue timeline for linked PR events

4. **Check the codebase**

   For issues reporting bugs or requesting specific changes:
   - Read the relevant code to determine if the described problem still exists
   - Run tests if applicable to verify the fix
   - Check git log for commits that reference the issue number

If there isnt enough to chew on from that, investigat high-signal queries like:
```
github-search_issues: query="repo:{owner}/{repo} is:issue is:open in:comments (fixed OR resolved OR closed)"
```

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
- Cap the report at 10 issues per run. If more qualify, prefer oldest issues first — they are highest priority for cleanup.
- Within the same age tier, order by confidence level (most confident first)
- Always include the specific evidence — don't just say "this looks resolved"
- Link to the resolving PR, commit, or code when possible
- If no issues qualify, call `noop` with message "No stale issues found — reviewed {analyzed_count}/{candidate_count} candidates ({total_open} open issues total)"

${{ inputs.additional-instructions }}
