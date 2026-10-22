---
inlined-imports: true
name: "Scheduled Audit"
description: "Generic scheduled audit — investigate the repository and file an issue when something needs attention"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/playwright-mcp-explorer.md
  - gh-aw-fragments/safe-output-scheduled-audit-issue.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  # Required on gh-aw >= v0.91.x: BYOK Copilot disables native web-fetch unless SDK mode is on.
  copilot-sdk: true
  model: ${{ inputs.model }}
on:
  stale-check: false
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      additional-instructions:
        description: "What the audit agent should investigate — appended as the Report Assignment"
        type: string
        required: true
      title-prefix:
        description: "Title prefix for created issues, e.g. '[my-audit]'"
        type: string
        required: true
      issue-label:
        description: "Label to apply to created issues (must already exist in the target repo)"
        type: string
        required: false
        default: ""
      setup-commands:
        description: "Shell commands to run before the agent starts (dependency install, build, etc.)"
        type: string
        required: false
        default: ""
      close-older-issues:
        description: "Retained for callers; ignored for compiler auto-close on gh-aw v0.92.5 (expressions rejected on safe-outputs.create-issue.close-older-issues). Previous findings are always listed so the agent can noop on duplicates. Automatic replacement of older issues is not available until expression support returns."
        type: boolean
        required: false
        default: false
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
      report-failure-as-issue:
        description: "When true, agent failures are reported as GitHub issues"
        type: boolean
        required: false
        default: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-scheduled-audit-${{ inputs.title-prefix }}
  cancel-in-progress: true
permissions:
  copilot-requests: write
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    min-integrity: approved
    trusted-users: ${{ inputs.allowed-bot-users }}
    toolsets: [repos, issues, pull_requests, search, labels, actions]
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
  - name: List previous findings
    env:
      GH_TOKEN: ${{ github.token }}
      TITLE_PREFIX: ${{ inputs.title-prefix }}
    run: |
      set -euo pipefail
      gh issue list \
        --repo "$GITHUB_REPOSITORY" \
        --search "in:title \"$TITLE_PREFIX\"" \
        --state all \
        --limit 100 \
        --json number,title,state \
        > /tmp/previous-findings.json || { echo "::warning::Failed to fetch previous findings — dedup will be skipped"; echo "[]" > /tmp/previous-findings.json; }
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

## Previous Findings

Always check `/tmp/previous-findings.json` for issues this agent has already filed before filing a new one. Previous findings are listed on every run (including when callers pass `close-older-issues: true`) because gh-aw v0.92.5 rejects expressions on `safe-outputs.create-issue.close-older-issues`, so compiler auto-close / replacement is not available.

- Run `cat /tmp/previous-findings.json` to read the list of previously filed issue numbers and titles.
- If your finding closely matches an open or recently-closed issue in that list, call `noop` instead of filing a duplicate.
- Only file a new issue when the finding is genuinely distinct from all previous findings.

### Labeling

If `${{ inputs.issue-label }}` is set and the label exists in the repository (check with `github-get_label`), include it in the `create_issue` call. Otherwise rely on the title prefix only.

${{ inputs.additional-instructions }}
