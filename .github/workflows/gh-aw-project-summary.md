---
description: "Create periodic project summary issues covering recent activity and priorities"
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
  group: project-summary
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
    title-prefix: "[project-summary] "
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

Create a periodic project summary with actionable highlights from recent activity.

### Data Gathering

1. **Find the last report**
   - Use `github-search_issues` with `repo:{owner}/{repo} is:issue in:title "[project-summary]"` sorted by `created` descending.
   - If a previous report exists, use its `createdAt` as the start date. Otherwise, use **14 days ago**.

2. **Collect activity since the start date**
   - `git log --since="<start-date>" --oneline --stat` for commit count and notable changes.
   - `github-search_issues` for issues created or updated since the start date (exclude project-summary issues).
   - `github-search_pull_requests` for PRs created since the start date.
   - `github-search_pull_requests` for PRs merged since the start date.
   - `github-search_pull_requests` for open PRs updated in the last 14 days.

3. **Identify candidate items**
   - PRs ready to merge or awaiting review.
   - Urgent or blocking issues (labels like `urgent`, `blocking`, `priority`, `P0`, `P1`).
   - Decisions needed (labels like `needs decision`, `discussion`, `question`).
   - Stale items: open issues or PRs with no updates in 30+ days.

### Activity Threshold (Noop)

Call `noop` with message **"Project summary skipped — no meaningful activity since last report"** when:
- Total activity (commits + new issues + new PRs + merged PRs) since the last report is fewer than **3**, and
- There are **no** urgent, decision-needed, or stale items.

### Issue Format

**Issue title:** `Project Summary - YYYY-MM-DD`

**Issue body:**

> ## Project Summary
> **Period:** [start date] to [today]
>
> ### 🎯 Easy Pickings
> - [PRs ready to merge, issues to close, quick wins]
>
> ### 🚨 Urgent Items
> - [Blocking items needing immediate attention]
>
> ### 📋 Decisions Needed
> - [Items requiring maintainer input]
>
> ### 🔄 Stale Items
> - [Issues/PRs with no updates in 30+ days]
>
> ### ✅ Recent Progress
> - [Merged PRs, closed issues, notable commits]
>
> ### 💡 Next Steps
> - [Prioritized recommendations]

**Guidelines:**
- Include direct links to issues/PRs and a short rationale for each item.
- If a section is empty, write `None`.
- Do not repeat items already covered in the previous report unless status materially changed.

${{ inputs.additional-instructions }}
