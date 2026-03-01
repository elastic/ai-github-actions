---
inlined-imports: true
name: "Stale Issues Remediator"
description: "Process stale-labeled issues: handle objections and close after 30-day grace period"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
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
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-stale-issues-remediator
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
tools:
  github:
    toolsets: [repos, issues, search]
  bash: true
strict: false
safe-outputs:
  activation-comments: false
  noop:
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
timeout-minutes: 30
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
        gh api --paginate "repos/$GITHUB_REPOSITORY/issues/$num/events" 2>/dev/null \
          | jq --arg lbl "$STALE_LABEL" --argjson num "$num" \
            '[.[] | select((.event=="labeled" or .event=="unlabeled") and .label.name==$lbl) | {number: $num, event: .event, created_at: .created_at}]' \
          || echo "[]"
      done | jq -s 'add // []' > /tmp/stale-label-events.json || echo "[]" > /tmp/stale-label-events.json
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Process open issues that carry the `${{ inputs.stale-label }}` label. Handle objections by removing the label, and close issues whose grace period has expired.

### Data Files

A prep step has already fetched:
- `/tmp/stale-labeled-issues.json` — all open issues labeled `${{ inputs.stale-label }}` (fields: number, title, updatedAt, labels, createdAt)
- `/tmp/stale-recent-comments.json` — the last 5 comments on each stale-labeled issue (fields: author, createdAt, body)
- `/tmp/stale-label-events.json` — label add/remove timeline events (fields: number, event, created_at)

Start by reading these files to get an overview. If `/tmp/stale-labeled-issues.json` is empty or contains zero issues, call `noop` with message "No stale-labeled issues to process" and stop.

### Processing Rules

For each open issue labeled `${{ inputs.stale-label }}`, fetch the full comment thread via `issue_read` with method `get_comments` and check in this order:

1. **"Not stale" objections** — If any comment posted **after** the `${{ inputs.stale-label }}` label was most recently added contains phrases like "not stale", "still relevant", "still needed", "still an issue", or "still a problem" (case-insensitive), call `remove_labels` to remove the `${{ inputs.stale-label }}` label from the issue.
   Skip this issue from closure — the objection overrides the stale determination.

2. **30-day expiry** — For issues with no such objection, compute the last labeled timestamp from `/tmp/stale-label-events.json` (find the most recent `"labeled"` event after any later `"unlabeled"` event for that issue number). If the label was added **30 or more days ago**, close the issue using `close_issue` with a comment explaining:

   > This issue was labeled `${{ inputs.stale-label }}` on [date] and has had no further activity for 30 days. Closing automatically. If this issue is still relevant, please reopen it.

   Skip issues where the label was added fewer than 30 days ago.

3. **Still in grace period** — Issues where the label was added fewer than 30 days ago and no objection exists require no action. Skip them silently.

### Completion

After processing all stale-labeled issues, if no actions were taken (no labels removed, no issues closed), call `noop` with message "Processed {count} stale-labeled issues — none ready for action (all within 30-day grace period)".

${{ inputs.additional-instructions }}
