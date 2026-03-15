---
inlined-imports: true
name: "Docs Patrol"
description: "Detect code changes that require documentation updates and file issues"
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
      lookback-window:
        description: "Git lookback window for detecting recent commits (e.g. '7 days ago', '14 days ago')"
        type: string
        required: false
        default: "7 days ago"
      title-prefix:
        description: "Title prefix for created issues (e.g. '[docs-patrol]')"
        type: string
        required: false
        default: "[docs-patrol]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-docs-patrol
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
    close-older-key: "${{ inputs.title-prefix }}"
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

Detect documentation drift — code changes that require corresponding documentation updates.

### Data Gathering

Use a lookback window of `--since="${{ inputs.lookback-window }}"` for all runs (scheduled and manual).

1. Run `git log --since="${{ inputs.lookback-window }}" --oneline --stat` to get a summary of recent commits. If there are no commits in the lookback window, report no findings and stop.
2. Discover documentation files dynamically — scan the repository for common doc locations: `README.md`, `CONTRIBUTING.md`, `DEVELOPING.md`, `docs/`, `documentation/`, and any `.md` files in the repository root. Do not assume a fixed directory structure.

### What to Look For

For each commit (or group of related commits), determine whether the changes could require documentation updates. Focus on:

1. **Public API changes** — new, renamed, or removed functions, endpoints, CLI flags, configuration options, or workflow inputs/outputs
2. **Behavioral changes** — altered defaults, changed error messages, modified control flow that affects user-facing behavior
3. **New features or workflows** — anything a user or contributor would need to know about
4. **Dependency or tooling changes** — version bumps, new dependencies, changed build/test commands
5. **Structural changes** — moved, renamed, or deleted files that are referenced in documentation
6. **Configuration changes** — new environment variables, changed file formats, altered directory structures

### Parallel Analysis

Use the **Pick Three, Keep Many** pattern for the analysis: spawn 3 `general-purpose` sub-agents, each analyzing the recent commits from a different angle (e.g., one checking public API and behavioral changes, one checking structural and configuration changes, one checking new features and dependency updates). Include the git log output, commit diffs, documentation file inventory, and the full "What to Look For" / "What to Skip" criteria in each sub-agent prompt. Each sub-agent should return all findings that meet the quality criteria.

### How to Analyze

For each potentially impactful change:
- Read the full diff to understand what changed
- Read the current documentation files to understand what's documented
- Check whether the relevant documentation was already updated in the same commit or a subsequent commit within the lookback window
- Check whether an open issue or PR already tracks the documentation update

### What to Skip

- Purely internal refactors with no user-facing impact
- Changes where documentation was already updated in the same or a later commit
- Changes where an open issue or PR already tracks the documentation update
- Test-only changes
- Minor changes where the existing docs are still substantially correct (e.g., a new optional parameter with a sensible default)
- Changes that only affect internal implementation details not referenced in any documentation

### Quality Gate — When to Noop

**Noop is the expected outcome most days.** Only file an issue when:
- The documentation is **concretely wrong** — a user following the docs would get incorrect results or errors
- A **new public feature** has zero documentation
- A **removed or renamed** public interface is still referenced in docs

Do not file for: vague "could be improved" suggestions, minor wording drift, or documentation that is slightly imprecise but still functionally correct.

### Issue Format

**Issue title:** Brief summary of what's out of date (e.g., "Update README for new CLI flag")

**Issue body:**

> Recent code changes in the repository have introduced documentation drift. The following changes need corresponding documentation updates.
>
> ## Changes Requiring Documentation Updates
>
> ### 1. [Brief description of the change]
>
> **Commit(s):** [SHA(s) with links]
> **What changed:** [Concise description of the code change]
> **Documentation impact:** [Which doc file(s) need updating and what specifically needs to change]
>
> ### 2. [Next change...]
>
> ## Suggested Actions
>
> - [ ] [Specific, actionable checkbox for each documentation update needed]

${{ inputs.additional-instructions }}
