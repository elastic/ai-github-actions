---
description: "Detect undocumented breaking changes in public interfaces"
imports:
  - gh-aw-fragments/elastic-tools.md
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
  group: breaking-change-detect
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
    title-prefix: "[breaking-change] "
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

Detect unintended breaking changes introduced in the last day that were not documented in PR descriptions, release notes, or repo documentation.

### Data Gathering

Determine the lookback window based on the current day of the week:
- **Monday**: Use `--since="3 days ago"` to capture Friday, Saturday, and Sunday
- **Tuesday through Friday**: Use `--since="1 day ago"` to capture the previous day
- **Manual trigger** (`workflow_dispatch`): Use `--since="1 day ago"`

Run `git log --since="<window>" --oneline --stat` to get a summary of recent commits. If there are no commits in the lookback window, call `noop` and stop.

For each commit (or cluster of related commits):
- Review the full diff (`git show <sha>` or `git diff <sha>^!`) to understand what changed.
- Map commits to PRs using `github-search_pull_requests` with query `repo:elastic/ai-github-actions sha:<sha>`.
- Read the PR body and related discussion for documentation or migration notes.
- Check for documentation updates in README, DEVELOPING, RELEASE, gh-agent-workflows/README, or any `CHANGELOG*` files (if present).

### What to Look For

Focus on clearly public interface or behavior breaks, such as:
1. **Workflow interface changes** — removed/renamed workflows, inputs, outputs, triggers, permissions, or schedules used by downstream repos.
2. **Composite action changes** — removed/renamed inputs/outputs, changed required env vars, altered default behavior.
3. **Documented guarantees** — changes that contradict or break behavior explicitly described in README/DEVELOPING/RELEASE.

### How to Decide "Undocumented"

A breaking change is **undocumented** if none of the following mention the break or migration steps:
- PR title/body or linked discussion
- RELEASE.md or any release notes in the lookback window
- README/DEVELOPING or other documentation updated in the same PR/commit set

### What to Skip

- Internal refactors with no public impact
- Changes that already include documentation or migration notes
- Test-only changes
- Changes already tracked by an open issue or PR

### Issue Format

**Issue title:** Undocumented breaking changes detected (date)

**Issue body:**

> Recent commits introduced breaking changes that appear undocumented.
>
> ## Breaking Changes
> 
> ### 1. [Brief description]
> **Commit(s):** [SHA(s) with links]
> **PR:** [Link]
> **What broke:** [Concise description]
> **Evidence:** [Diff or file references]
> **Why undocumented:** [Where documentation is missing]
> **Suggested fix:** [Docs update or migration note]
>
> ## Suggested Actions
> - [ ] Document each breaking change (README/DEVELOPING/RELEASE or release notes)
> - [ ] Add migration guidance where needed

${{ inputs.additional-instructions }}
