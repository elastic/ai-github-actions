---
inlined-imports: true
name: "UX Design Patrol"
description: "Detect UI/UX design drift in recent commits and file a consolidation report"
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
  - gh-aw-fragments/best-of-three.md
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
      lookback-window:
        description: "Git lookback window for detecting recent commits (e.g. '7 days ago', '14 days ago')"
        type: string
        required: false
        default: "7 days ago"
      title-prefix:
        description: "Title prefix for created issues (e.g. '[ux-design-patrol]')"
        type: string
        required: false
        default: "[ux-design-patrol]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ux-design-patrol
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
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Detect UX design drift — recent commits that introduce new UI or user-facing patterns that duplicate or conflict with patterns already established elsewhere in the codebase.

### Data Gathering

Use a lookback window of `--since="${{ inputs.lookback-window }}"` for all runs (scheduled and manual).

1. Run `git log --since="${{ inputs.lookback-window }}" --oneline --stat` to get a summary of recent commits. If there are no commits in the lookback window, report no findings and stop.
2. For each commit, read the full diff to understand what user-facing patterns were added or changed.
3. Discover existing user-facing patterns in the codebase dynamically — search for related code in source files, templates, and configuration that handles output, prompts, messages, or other user interactions.

### What to Look For

Focus on places where a recent commit introduces a user-facing pattern that already exists elsewhere in a different form — where consolidation would benefit the user experience. Examples include:

1. **Output and message formatting** — a new command prints a table differently than existing tables; a new error message uses a different style than the established error format; progress indicators use a different style than elsewhere
2. **Confirmation and prompt dialogs** — a new interactive prompt uses different wording, ordering, or structure from existing prompts (e.g., `[y/N]` vs `[yes/no]`)
3. **CLI flag and option naming** — a new flag uses a different naming convention (`--dry-run` vs `--dryRun` vs `--no-execute`) or a different value format than existing flags for the same concept
4. **Status and state representation** — a new feature displays status (enabled/disabled, active/inactive, true/false) differently from how status is shown elsewhere
5. **Help text and usage strings** — new help text uses a different structure, tone, or level of detail than existing help text
6. **Date, time, and number formatting** — a new output formats timestamps or numeric values differently from the established format
7. **Color, icon, and symbol usage** — a new UI element uses different colors, symbols, or emoji for the same semantic meaning as existing elements
8. **Loading and progress indicators** — a new operation shows progress differently (spinner vs dots vs percentage) from existing operations

### How to Analyze

For each potentially impactful change:
- Read the full diff to understand what user-facing pattern was introduced
- Search the codebase for similar patterns — look for the same type of output, message, prompt, or UI element elsewhere
- Compare the new pattern to the existing ones to determine whether they are meaningfully inconsistent
- Check whether an open issue or PR already tracks the consolidation

### What to Skip

- Internal implementation details with no user-facing output
- Changes where the new pattern is intentionally different (e.g., a separate UI context, a deliberate redesign, a different audience)
- Trivial differences that would not confuse or frustrate a user (e.g., minor whitespace differences)
- Changes that already align with the established pattern
- Changes where an open issue or PR already tracks the consolidation
- Cases where no existing pattern exists to compare against

### Quality Gate — When to Noop

**Noop is the expected outcome most days.** Only file an issue when:
- A **concrete, specific inconsistency** exists — you can name the exact files, functions, or output strings that conflict
- The inconsistency would be **noticeable to a user** — they would encounter both patterns in normal use
- **Consolidation is clearly feasible** — the patterns are close enough that a maintainer could reasonably unify them

Do not file for: subjective style preferences, theoretical future inconsistencies, or cases where the difference is intentional or negligible.

### Issue Format

**Issue title:** Brief summary of the design drift (e.g., "Inconsistent error message format across CLI commands")

**Issue body:**

> Recent commits have introduced UI/UX patterns that diverge from established patterns elsewhere in the codebase. The following inconsistencies reduce design consistency for users.
>
> ## Design Drift Findings
>
> ### 1. [Brief description of the inconsistency]
>
> **Commit(s):** [SHA(s) with links]
> **New pattern (introduced by commit):**
> ```
> [example of the new pattern — output, code, or config]
> ```
> **Existing pattern (established elsewhere):**
> ```
> [example of the existing pattern — output, code, or config]
> ```
> **Location of new pattern:** [file path(s)]
> **Location of existing pattern:** [file path(s)]
> **User impact:** [brief explanation of how this inconsistency affects users]
>
> ### 2. [Next finding...]
>
> ## Suggested Actions
>
> - [ ] [Specific, actionable checkbox for each consolidation needed]

${{ inputs.additional-instructions }}
