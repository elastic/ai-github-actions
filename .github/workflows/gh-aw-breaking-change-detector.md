---
inlined-imports: true
name: "Breaking Change Detector"
description: "Detect undocumented breaking changes in public interfaces"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/ensure-full-history.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/pick-three-keep-many.md
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
      title-prefix:
        description: "Title prefix for created issues (e.g. '[breaking-change]')"
        type: string
        required: false
        default: "[breaking-change]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: breaking-change-detector
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
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
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
- Map commits to PRs using `github-search_pull_requests` with query `repo:{owner}/{repo} sha:<sha>`.
- Read the PR body and related discussion for documentation or migration notes.
- Check for documentation updates in README, DEVELOPING, RELEASE, gh-agent-workflows/README, or any `CHANGELOG*` files (if present).

Use the **Pick Three, Keep Many** pattern for the analysis: spawn 3 `general-purpose` sub-agents, each analyzing the recent commits from a different angle (e.g., one checking workflow/action interface changes, one checking documented guarantees, one checking downstream compatibility). Include the git log output, commit diffs, repo conventions, and the full "What to Look For" criteria in each sub-agent prompt. Each sub-agent should return all findings that meet the quality criteria.

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
- Additive changes that don't break existing consumers (new optional inputs with defaults, new workflows, new outputs)
- Changes to internal/private interfaces not consumed by downstream repos

### Quality Gate — When to Noop

**Noop is the expected outcome most days.** Only file an issue when you can demonstrate a concrete break:
- A downstream consumer using the documented interface would **fail or get wrong results** after this change.
- You can identify the **specific interface contract** that was broken (removed input, changed type, renamed workflow, etc.).
- The break is **not documented** anywhere in the PR, release notes, or repo docs.

Do not file for: speculative breaks ("this might affect someone"), internal restructuring, or changes where backward compatibility is maintained (even if the approach changed).

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
