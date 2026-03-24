---
inlined-imports: true
name: "Estc Docs Patrol External"
description: "Detect code changes that require updates to published Elastic documentation"
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
        description: "Allowed bot actor usernames (comma-separated)"
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
        description: "Title prefix for created issues (e.g. '[docs-patrol-external]')"
        type: string
        required: false
        default: "[docs-patrol-external]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-estc-docs-patrol-external
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
mcp-servers:
  elastic-docs:
    url: "https://www.elastic.co/docs/_mcp/"
    allowed:
      - "SemanticSearch"
      - "GetDocumentByUrl"
      - "FindRelatedDocs"
      - "FindInconsistencies"
network:
  allowed:
    - "www.elastic.co"
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

Detect drift between code changes and published Elastic documentation — changes that require updates to `elastic.co/docs`, `applies_to` tags, or backports to earlier version branches.

### Data Gathering

Use a lookback window of `--since="${{ inputs.lookback-window }}"` for all runs (scheduled and manual).

1. Run `git log --since="${{ inputs.lookback-window }}" --oneline --stat` to get a summary of recent commits. If there are no commits in the lookback window, report no findings and stop.
2. Discover documentation files dynamically — scan the repository for common doc locations: `README.md`, `CONTRIBUTING.md`, `DEVELOPING.md`, `docs/`, `documentation/`, and any `.md` files in the repository root. Do not assume a fixed directory structure.

### What to Look For

For each commit (or group of related commits), determine whether the changes could require updates to published Elastic documentation. Focus on:

1. **Public API changes** — new, renamed, or removed functions, endpoints, CLI flags, configuration options, or workflow inputs/outputs.
2. **Behavioral changes** — altered defaults, changed error messages, modified control flow that affects user-facing behavior.
3. **New features or workflows** — anything that should be reflected in published documentation.
4. **Feature lifecycle changes** — features moving between lifecycle states (preview, beta, GA, deprecated, removed) that require `applies_to` tag updates.
5. **Version-sensitive changes** — bug fixes or behavioral changes that apply to multiple release branches and may need documentation backports.

### How to Analyze

For each potentially impactful change:
- Read the full diff to understand what changed.
- Check whether an open issue or PR already tracks the external documentation update.

#### Check published Elastic documentation

Use the `elastic-docs` MCP server to check whether the change affects published documentation on `elastic.co/docs`:
- Call `SemanticSearch` or `FindRelatedDocs` with a description of the changed functionality to find published pages that document it.
- If published pages are found, check whether the code change makes them inaccurate or incomplete.
- Call `GetDocumentByUrl` to read specific published pages when you need to verify details.

Only flag published docs drift when the code change **concretely contradicts** what's published. Do not flag pages that are merely related.

#### Check `applies_to` tags

When a code change affects feature availability or lifecycle:
- Check whether documentation files in the repository use `applies_to` frontmatter metadata.
- If they do, verify the tags still reflect reality after the code change. For example:
  - A feature graduating from beta to GA needs its `applies_to` lifecycle updated.
  - A feature being deprecated or removed needs corresponding tag changes.
  - A new feature needs `applies_to` tags on its documentation page.
- Note the specific `applies_to` changes needed in the issue.

#### Check backport needs

When a code change fixes a bug or changes behavior in a way that affects documentation:
- Check if the change targets a release branch or is cherry-picked from one.
- If the fix applies to earlier versions, note whether the documentation update needs to be backported (e.g., the fix applies to both 9.x and 8.x, so docs for both versions may need updating).
- If the repository uses `applies_to` version ranges, note whether the version range needs adjusting.

### What to Skip

- Changes with no impact on published external documentation.
- Changes where an open issue or PR already tracks the external documentation update.
- Test-only or internal-only changes.
- Changes where published docs are still substantially correct (e.g., a new optional parameter with a sensible default).
- Purely internal refactors with no user-facing impact.

### Quality Gate — When to Noop

**Noop is the expected outcome most days.** Only file an issue when:
- Published Elastic documentation **directly contradicts** the current code behavior.
- An `applies_to` tag is **demonstrably incorrect** after a lifecycle change (e.g., a feature tagged as `beta` that has been promoted to `ga`).
- A **new public feature** has zero coverage in published documentation.
- A documentation backport is **concretely needed** for an earlier version branch.

Do not file for: vague "could be improved" suggestions, minor wording drift, documentation that is slightly imprecise but still functionally correct, or speculative backport needs.

### Issue Format

**Issue title:** Brief summary of what's out of date (e.g., "Update elastic.co docs for new CLI flag")

**Issue body:**

> Recent code changes require updates to published Elastic documentation.
>
> ## Changes Requiring External Documentation Updates
>
> ### 1. [Brief description of the change]
>
> **Commit(s):** [SHA(s) with links]
> **What changed:** [Concise description of the code change]
> **Published docs impact:** [Which elastic.co/docs pages are affected, with URLs]
> **`applies_to` impact:** [If applicable — which tags need updating and why]
> **Backport needed:** [If applicable — which earlier versions are affected and why]
>
> ### 2. [Next change...]
>
> ## Suggested Actions
>
> - [ ] [Specific, actionable checkbox for each documentation update needed]

${{ inputs.additional-instructions }}
