---
inlined-imports: true
name: "Code Duplication Fixer"
description: "Fix code-duplication-detector issues by consolidating duplicates and opening a focused PR"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
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
      draft-prs:
        description: "Whether to create pull requests as drafts"
        type: boolean
        required: false
        default: true
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: code-duplication-fixer
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
  serena: ["go", "python", "typescript", "java", "csharp", "rust"]
strict: false
safe-outputs:
  noop:
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

### Candidate Search

Search for open Code Duplication Detector issues:

````text
github-search_issues: query="repo:{owner}/{repo} is:issue is:open (label:refactor OR in:title \"[refactor]\") sort:updated-asc"
````

### Implementation

Each fix must be a safe, behavior-preserving refactor — no functional changes.

1. Read the affected files and understand the duplication or misplacement.
2. Use Serena tools (`find_symbol`, `find_referencing_symbols`, `search_for_pattern`) to find all callers and references.
3. Consolidate duplicates into a single shared function, or move the misplaced function to its correct home.
4. Update all callers to use the consolidated/moved function.
5. Run the most relevant targeted tests. **Tests must pass.**
6. Commit the changes locally.

${{ inputs.additional-instructions }}
