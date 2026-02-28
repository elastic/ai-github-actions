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
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/scheduled-audit.md
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
      stale-label:
        description: "Label used to mark stale issues"
        type: string
        required: false
        default: "stale"
      title-prefix:
        description: "Title prefix for created issues (e.g. '[stale-issues]')"
        type: string
        required: false
        default: "[stale-issues]"
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
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-issues: true
    expires: 7d
  add-labels:
    max: 10
    target: "*"
    allowed:
      - "${{ inputs.stale-label }}"
  remove-labels:
    max: 10
    target: "*"
    allowed:
      - "${{ inputs.stale-label }}"
  close-issue:
    max: 10
    target: "*"
    required-labels:
      - "${{ inputs.stale-label }}"
timeout-minutes: 60
steps:
  - name: Collect stale-labeled issues
    env:
      GH_TOKEN: ${{ github.token }}
      STALE_LABEL: ${{ inputs.stale-label }}
    run: |
      set -euo pipefail

      # Fetch all open issues carrying the stale label
      gh issue list \
        --repo "$GITHUB_REPOSITORY" \
        --label "$STALE_LABEL" \
        --state open \
        --limit 200 \
        --json number,title,updatedAt,labels,createdAt \
        > /tmp/stale-labeled-issues.json || { echo "::warning::Failed to fetch stale-labeled issues"; echo "[]" > /tmp/stale-labeled-issues.json; }

      echo "Stale-labeled issues: $(jq length /tmp/stale-labeled-issues.json)"

      # For each stale-labeled issue, grab recent comments and label timeline events.
      jq -c '.[]' /tmp/stale-labeled-issues.json | while IFS= read -r issue; do
        num=$(echo "$issue" | jq -r '.number')
        gh issue view "$num" \
          --repo "$GITHUB_REPOSITORY" \
          --json comments \
          --jq '.comments[-5:] | .[] | {author: .author.login, createdAt: .createdAt, body: .body[0:500]}' \
          2>/dev/null || true
      done | jq -s '.' > /tmp/stale-recent-comments.json || echo "[]" > /tmp/stale-recent-comments.json

      # Fetch label add/remove events for each stale-labeled issue (for 30-day expiry)
      jq -r '.[].number' /tmp/stale-labeled-issues.json | while IFS= read -r num; do
        gh api "repos/$GITHUB_REPOSITORY/issues/$num/events" \
          --jq --arg lbl "$STALE_LABEL" \
          '[.[] | select((.event=="labeled" or .event=="unlabeled") and .label.name==$lbl) | {number: '"$num"', event: .event, created_at: .created_at}]' \
          2>/dev/null || echo "[]"
      done | jq -s 'add // []' > /tmp/stale-label-events.json || echo "[]" > /tmp/stale-label-events.json

  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Find open issues that are very likely already resolved. This workflow operates in two phases:

1. **Close phase** — Close issues that have carried the `${{ inputs.stale-label }}` label for 30+ days without the label being removed.
2. **Tag phase** — Label newly identified stale candidates with the `${{ inputs.stale-label }}` label and file a report.

Run both phases on every invocation, starting with the close phase.

### Phase 1: Process stale-labeled issues

A prep step has already fetched stale-labeled issues to `/tmp/stale-labeled-issues.json` (fields: number, title, updatedAt, labels, createdAt), recent comments to `/tmp/stale-recent-comments.json`, and label timeline events to `/tmp/stale-label-events.json` (each entry has `number`, `event` ("labeled"/"unlabeled"), and `created_at`). Start by reading these files to get an overview.

Then search for open issues labeled `${{ inputs.stale-label }}`:
```
github-search_issues: query="repo:{owner}/{repo} is:issue is:open label:${{ inputs.stale-label }}"
```

For each result, fetch the full comment thread via `issue_read` with method `get_comments` and check for two things:

1. **"Not stale" objections** — If any comment posted **after** the `${{ inputs.stale-label }}` label was most recently added contains phrases like "not stale", "still relevant", "still needed", "still an issue", or "still a problem" (case-insensitive), call `remove_labels` to remove the `${{ inputs.stale-label }}` label from the issue.
   Skip this issue from closure — the objection overrides the stale determination.

2. **30-day expiry** — For issues with no such objection, compute the last labeled timestamp from `/tmp/stale-label-events.json` (find the most recent `"labeled"` event after any later `"unlabeled"` event for that issue number). If the label was added **30 or more days ago**, close the issue using `close_issue` with a comment explaining:

   > This issue was labeled `${{ inputs.stale-label }}` on [date] and has had no further activity for 30 days. Closing automatically. If this issue is still relevant, please reopen it.

   Skip issues where the label was added fewer than 30 days ago.

### Phase 2: Identify and tag new stale candidates

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

If there isn't enough from that, investigate high-signal queries like:
```
github-search_issues: query="repo:{owner}/{repo} is:issue is:open in:comments (fixed OR resolved OR closed)"
```

### What Qualifies as "Very Likely Resolved"

Only flag an issue if you have **strong evidence** from at least one of these categories:

1. **Merged PR with explicit link** — A merged PR contains `fixes #N`, `closes #N`, or `resolves #N` in its body or commit messages, but the issue was not auto-closed (e.g., PR targeted a non-default branch)
2. **Code evidence** — The specific bug, missing feature, or requested change described in the issue is verifiably addressed in the current codebase. You must confirm this by reading the relevant code.
3. **Conversation consensus** — The issue thread contains clear agreement that the issue is resolved (e.g., the reporter confirmed the fix, a maintainer said "this is done"), but nobody closed it

### What to Skip

- Issues already labeled `${{ inputs.stale-label }}` — they are already tracked and will be closed automatically after 30 days
- Issues with recent activity (comments in the last 14 days) — someone is still working on them
- Issues labeled `epic`, `tracking`, `umbrella`, or similar meta-labels — these are intentionally kept open
- Issues where the resolution is ambiguous or you aren't sure
- Feature requests where you can't definitively confirm implementation
- Issues with open/unmerged PRs linked — work may still be in progress

**When in doubt, skip the issue.** False positives waste maintainer time and erode trust in the report. Only include issues where you are highly confident they are resolved.

### Labeling

For each issue included in the report, call `add_labels` with the `${{ inputs.stale-label }}` label on that issue. This starts the 30-day grace period — maintainers can remove the label to prevent automatic closure.

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
- Cap the report at 10 stale issues per run. If more qualify, prefer oldest issues first — they are highest priority for cleanup.
- Within the same age tier, order by confidence level (most confident first)
- Always include the specific evidence — don't just say "this looks resolved"
- Link to the resolving PR, commit, or code when possible
- If no issues qualify for tagging or closing, call `noop` with message "No stale issues found — reviewed {analyzed_count}/{candidate_count} candidates ({total_open} open issues total), closed {closed_count} previously stale issues"

${{ inputs.additional-instructions }}
