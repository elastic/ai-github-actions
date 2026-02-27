---
inlined-imports: true
name: "Scheduled Fix"
description: "Generic scheduled fixer — pick up an open issue and create a focused PR that addresses it"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-pr.md
  - gh-aw-fragments/scheduled-fix.md
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
        description: "Domain-specific fix instructions — appended as the Fix Assignment"
        type: string
        required: true
      title-prefix:
        description: "Title prefix to search for in open issues, e.g. '[text-auditor]'"
        type: string
        required: true
      issue-label:
        description: "Label to search for in open issues"
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
      draft-prs:
        description: "Whether to create pull requests as drafts"
        type: boolean
        required: false
        default: true
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: scheduled-fix-${{ inputs.title-prefix }}
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, actions]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  max-patch-size: 10240
  noop:
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
    run: eval "$SETUP_COMMANDS"
---

## Previous Findings

Before filing a new issue, check `/tmp/previous-findings.json` for issues this agent has already filed.

- Run `cat /tmp/previous-findings.json` to read the list of previously filed issue numbers and titles.
- If your finding closely matches an open or recently-closed issue in that list, call `noop` instead of filing a duplicate.
- Only file a new issue when the finding is genuinely distinct from all previous findings.

### Candidate Search

Search for open issues matching the configured title prefix:

````text
github-search_issues: query="repo:{owner}/{repo} is:issue is:open in:title \"${{ inputs.title-prefix }}\" sort:updated-asc"
````

If `${{ inputs.issue-label }}` is not empty, also search by label:

````text
github-search_issues: query="repo:{owner}/{repo} is:issue is:open label:${{ inputs.issue-label }} sort:updated-asc"
````

### Implementation

${{ inputs.additional-instructions }}
