---
description: "Check downstream users for required workflow ref updates and report by repository"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  workflow_call:
    inputs:
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
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: downstream-updates-needed
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
    - go
    - node
    - python
    - ruby
strict: false
safe-outputs:
  noop:
  create-issue:
    max: 1
    title-prefix: "[downstream-updates] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Workflow for checking downstream users of these actions (in the `elastic` and `strawgate` orgs) and seeing if their workflows need updates. Post an issue with the repo-by-repo updates required.

## Context

- **Repository**: ${{ github.repository }}
- **Data file**: `data/downstream-users.json`

## Step 1: Gather inputs

1. Read `data/downstream-users.json`.
2. Keep only entries where `repo` starts with `elastic/` or `strawgate/`.
3. Fetch latest release for `elastic/ai-github-actions` and capture:
   - `latest_version` (for example `v0.2.5`)
   - `recommended_floating_major` (for example `v0`)
4. If no matching downstream repos exist, call `noop` with a clear message.

## Step 2: Validate data model

The expected schema for each workflow entry is:

```json
{
  "workflow_file": ".github/workflows/example.yml",
  "uses_target": "workflows/pr-review/rwx",
  "ref": "v0"
}
```

If any downstream repo still has legacy string entries instead of objects, file an issue that explicitly says the downstream inventory must be regenerated with ref metadata before reliable update detection can run.

## Step 3: Determine update status

For each workflow entry, classify by `ref`:

1. **Floating major** (`v<major>`, e.g. `v0`)
   - If equal to `recommended_floating_major`, mark as up to date.
   - If different major, mark update needed to `recommended_floating_major`.

2. **Pinned semver tag** (`vX.Y.Z`)
   - Compare with `latest_version`.
   - If older, mark update needed to `latest_version`.

3. **Branch refs** (e.g. `main`, `master`, `release/*`)
   - Mark as policy warning and recommend `recommended_floating_major` or `latest_version`.

4. **SHA refs** (hex commit IDs)
   - Mark as informational, no forced update, include recommendation to review manually.

5. **Other refs**
   - Mark as review needed and include the raw ref.

## Step 4: Report

Create one issue grouped by repo. For each repo with findings, include a table:

- workflow file
- uses target
- current ref
- recommended ref
- reason

If every entry is up to date and has no warnings, call `noop` with:
`Downstream updates check complete — no updates needed.`

${{ inputs.additional-instructions }}
