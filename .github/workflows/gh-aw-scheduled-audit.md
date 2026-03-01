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
        description: "Close older issues when a new one is filed. When false (default), previous findings are checked to avoid duplicates. When true, the previous report is replaced by the new one."
        type: boolean
        required: false
        default: false
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
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-scheduled-audit-${{ inputs.title-prefix }}
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, labels, actions]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  noop:
timeout-minutes: 90
steps:
  - name: List previous findings
    if: ${{ !inputs.close-older-issues }}
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
    run: eval "$SETUP_COMMANDS"
---

## Previous Findings

When `close-older-issues` is `false` (current: `${{ inputs.close-older-issues }}`), check `/tmp/previous-findings.json` for issues this agent has already filed before filing a new one.

- Run `cat /tmp/previous-findings.json` to read the list of previously filed issue numbers and titles.
- If your finding closely matches an open or recently-closed issue in that list, call `noop` instead of filing a duplicate.
- Only file a new issue when the finding is genuinely distinct from all previous findings.

When `close-older-issues` is `true`, the previous findings check is not needed — any older open issue is automatically closed when a new one is filed.

### Labeling

If `${{ inputs.issue-label }}` is set and the label exists in the repository (check with `github-get_label`), include it in the `create_issue` call. Otherwise rely on the title prefix only.

${{ inputs.additional-instructions }}
