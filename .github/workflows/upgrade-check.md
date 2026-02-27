---
inlined-imports: true
name: "Internal: Upgrade Check"
description: "Check for gh-aw releases and assess whether our workflows need upgrading"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/pick-three-keep-one.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  schedule:
    - cron: "daily around 14:00 on weekdays"
  workflow_dispatch:
    inputs:
      title-prefix:
        description: "Title prefix for created issues"
        required: false
        default: "[gh-aw-upgrade]"
  roles: [admin, maintainer, write]
  bots:
    - "github-actions[bot]"
concurrency:
  group: upgrade-check
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
safe-outputs:
  noop:
  create-issue:
    max: 1
    title-prefix: "[gh-aw-upgrade] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 90
---

Check for recent gh-aw releases and determine if our workflows need upgrading or adjusting.

### Data Gathering

1. Read our current `Makefile` to find the pinned `GH_AW_VERSION` (e.g., `v0.44.0`).
2. Read all workflow files in `.github/workflows/gh-aw-*.md` to understand our current configuration — frontmatter fields, imports, safe-outputs, tools, network allows, and prompt patterns.
3. Fetch recent gh-aw releases using `gh api repos/github/gh-aw/releases?per_page=10` to get the last 10 releases. Identify all releases newer than our pinned version.
4. If we are already on the latest release, report no findings and stop.
5. For each newer release, read the release notes (the `body` field). Also fetch the CHANGELOG if needed: `web-fetch` from `https://raw.githubusercontent.com/github/gh-aw/main/CHANGELOG.md`.

### What to Look For

Compare the release notes and changelog entries against our workflow configurations. Focus on:

1. **Breaking changes** — removed or renamed frontmatter fields, changed compiler behavior, deprecated features we rely on
2. **New features we should adopt** — new frontmatter fields, new safe-outputs, new tools, new engine options that would benefit our workflows
3. **Bug fixes relevant to us** — fixes for issues we may be experiencing or working around
4. **Security improvements** — patches or hardening we should pick up
5. **Safe-output changes** — new safe-outputs, changed defaults, removed options
6. **Compiler changes** — new validation rules, changed strict mode behavior, new warnings that may affect our compilation

### How to Analyze

For each finding:
- Cross-reference against our actual workflow files to determine if the change is relevant to us
- Check if we use the affected feature/field/option
- Assess the upgrade urgency: critical (breaking/security), recommended (useful features/fixes), or informational (nice-to-know)
- If a breaking change affects us, describe specifically which workflow files need updating and how

### What to Skip

- Changes to gh-aw internals that don't affect workflow authors (compiler refactors, CI changes, test improvements)
- New features we have no use for based on our current workflow patterns
- Changes already addressed in our current configuration

### Issue Format

**Issue title:** "gh-aw upgrade available: [current version] → [latest version]"

**Issue body:**

> A new version of gh-aw is available. We are currently on `[current version]`, latest is `[latest version]`.
>
> ## Upgrade Assessment
>
> **Urgency:** [Critical / Recommended / Informational]
>
> ## Relevant Changes
>
> ### [version tag]
>
> #### Breaking Changes (if any)
> - **[change]**: [impact on our workflows and what needs updating]
>
> #### New Features Worth Adopting
> - **[feature]**: [what it does and which of our workflows would benefit]
>
> #### Bug Fixes
> - **[fix]**: [what was broken and whether it affects us]
>
> #### Security
> - **[patch]**: [what was addressed]
>
> ### [next version tag...]
>
> ## Upgrade Steps
>
> - [ ] Update `GH_AW_VERSION` in `Makefile` from `[current]` to `[latest]`
> - [ ] [Any workflow file changes needed for breaking changes]
> - [ ] Run `make compile` and verify 0 errors, 0 warnings
> - [ ] [Any other specific steps]
