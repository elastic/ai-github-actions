---
# DO NOT EDIT — this is a synced copy. Source: gh-agent-workflows/docs-drift.md
description: "Detect code changes that require documentation updates and file issues"
imports:
  - gh-aw-workflows/scheduled-report-rwx.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  schedule:
    - cron: "0 14 * * 1-5"
  workflow_dispatch:
concurrency:
  group: docs-drift
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  create-issue:
    max: 1
    title-prefix: "[docs-drift] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

Detect documentation drift — code changes that require corresponding documentation updates.

### Data Gathering

Determine the lookback window based on the current day of the week:
- **Monday**: Use `--since="3 days ago"` to capture Friday, Saturday, and Sunday
- **Tuesday through Friday**: Use `--since="1 day ago"` to capture the previous day
- **Manual trigger** (`workflow_dispatch`): Use `--since="1 day ago"`

Run `git log --since="<window>" --oneline --stat` to get a summary of recent commits. If there are no commits in the lookback window, report no findings and stop.

### What to Look For

For each commit (or group of related commits), determine whether the changes could require documentation updates. Focus on:

1. **Public API changes** — new, renamed, or removed functions, endpoints, CLI flags, configuration options, or workflow inputs/outputs
2. **Behavioral changes** — altered defaults, changed error messages, modified control flow that affects user-facing behavior
3. **New features or workflows** — anything a user or contributor would need to know about
4. **Dependency or tooling changes** — version bumps, new dependencies, changed build/test commands
5. **Structural changes** — moved, renamed, or deleted files that are referenced in documentation
6. **Configuration changes** — new environment variables, changed file formats, altered directory structures

### How to Analyze

For each potentially impactful change:
- Read the full diff to understand what changed
- Read the current documentation files (README, DEVELOPING, CONTRIBUTING, docs/, etc.) to understand what's documented
- Check whether the relevant documentation was already updated in the same commit or a subsequent commit within the lookback window
- Check whether an open issue or PR already tracks the documentation update

### What to Skip

- Purely internal refactors with no user-facing impact
- Changes where documentation was already updated in the same or a later commit
- Changes where an open issue or PR already tracks the documentation update
- Test-only changes

### Issue Format

**Issue title:** Brief summary of what's out of date (e.g., "Update README for new docs-drift workflow")

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
