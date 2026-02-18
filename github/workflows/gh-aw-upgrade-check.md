---
description: "Check for gh-aw releases and assess whether our workflows need upgrading"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  schedule:
    - cron: "daily around 14:00 on weekdays"
  workflow_dispatch:
concurrency:
  group: gh-aw-upgrade-check
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
  messages:
    footer: "---\n[What is this?](https://ela.st/github-ai-tools) | [From workflow: {workflow_name}]({run_url})\n\nGive us feedback! React with 🚀 if perfect, 👍 if helpful, 👎 if not."
  noop:
  create-issue:
    max: 1
    title-prefix: "[gh-aw-upgrade] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

Check for recent gh-aw releases and determine if our workflows need upgrading or adjusting.

A footer is automatically appended to all comments and reviews. Do not add your own footer or sign-off — the runtime handles this.

### Data Gathering

1. Read our current `Makefile` to find the pinned `GH_AW_VERSION` (e.g., `v0.44.0`).
2. Read all workflow files in `.github/workflows/gh-aw-*.md` to understand our current configuration — frontmatter fields, imports, safe-outputs, tools, network allows, and prompt patterns.
3. Fetch recent gh-aw releases using `gh api repos/github/gh-aw/releases?per_page=10` to get the last 10 releases. Identify all releases newer than our pinned version.
4. If we are already on the latest release, report no findings and stop.
5. For each newer release, read the release notes (the `body` field). Also fetch the CHANGELOG if needed: `web-fetch` from `https://raw.githubusercontent.com/github/gh-aw/main/CHANGELOG.md`.

### What to Look For

Compare the release notes and changelog entries against our workflow configurations. Focus on:

1. **Recommendation** — upgrade now/delay/skip based on impact to our current workflows
2. **Upgrade risks** — breaking changes or behavior shifts that would cause problems in our existing workflows
3. **Features to adopt** — new capabilities that map directly to how we use gh-aw today
4. **Supporting evidence** — only the specific release notes that justify the recommendation, risks, and features

### How to Analyze

For each finding:
- Cross-reference against our actual workflow files to determine if the change is relevant to us
- Identify concrete risks and features tied to our current workflow usage (name the workflows/fields)
- Decide the recommendation (upgrade now/delay/skip) and keep the rationale short
- Exclude anything that does not directly affect our workflows

### What to Skip

- Changes to gh-aw internals that don't affect workflow authors (compiler refactors, CI changes, test improvements)
- New features we have no use for based on our current workflow patterns
- Changes already addressed in our current configuration

### Issue Format

**Issue title:** "gh-aw upgrade available: [current version] → [latest version]"

**Issue body:**

> A new version of gh-aw is available. We are currently on `[current version]`, latest is `[latest version]`.
>
> ## Recommendation
>
> **[Upgrade now / Delay / Skip]** — [brief rationale tied to our workflows]
>
> ## Upgrade Risks
>
> - **[risk]**: [what breaks or changes, and which workflow(s) it impacts]
>
> ## Features to Adopt
>
> - **[feature]**: [what it enables and which workflow(s) benefit]
>
> ## Relevant Changes
>
> ### [version tag]
>
> - **[change]**: [only the items that support the recommendation, risks, or features]
>
> ### [next version tag...]
>
> ## Upgrade Steps
>
> - [ ] Update `GH_AW_VERSION` in `Makefile` from `[current]` to `[latest]`
> - [ ] [Any workflow file changes needed for breaking changes]
> - [ ] Run `make compile` and verify 0 errors, 0 warnings
> - [ ] [Any other specific steps]
