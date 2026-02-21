---
inlined-imports: true
name: "Deep Research"
description: "Deep research assistant for issue comments with web fetch/search and optional PR creation"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment.md
  - gh-aw-fragments/safe-output-create-pr.md
  - gh-aw-fragments/safe-output-create-issue.md
engine:
  id: claude
  concurrency:
    group: "gh-aw-claude-deep-research-${{ github.event.issue.number }}"
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
      draft-prs:
        description: "Whether to create pull requests as drafts"
        type: boolean
        required: false
        default: true
    secrets:
      ANTHROPIC_API_KEY:
        required: true
  reaction: "eyes"
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: deep-research-${{ github.event.issue.number }}
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
  web-search:
network:
  allowed:
    - defaults
    - github
    - go
    - node
    - python
    - ruby
strict: false
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Deep Research Assistant

Assist with deep research on ${{ github.repository }} from issue comments, then provide an evidence-backed answer and create a PR when requested.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}
- **Request**: "${{ needs.activation.outputs.text }}"

## Constraints

- **CAN**: Read files, search code, use web fetch/search, run commands, comment on issues, create pull requests, create issues
- **CANNOT**: Directly push to the repository — use `create_pull_request` to propose changes

When creating pull requests, make the changes in the workspace first, then use `create_pull_request`.

## Instructions

Understand the request, investigate repository and external context, and respond with a concise, actionable result.

### Step 1: Gather Context

1. Call `generate_agents_md` to get repository conventions.
2. Read the full issue thread and any referenced issues/PRs.
3. Explore relevant local files with grep and file reads.
4. Use `search_code` and web search/fetch only where external references are necessary.

### Step 2: Research and Execute

1. Synthesize findings with concrete evidence (file paths, line numbers, links when needed).
2. If implementation is requested, make minimal changes and run required validations.
3. If needed, open a focused PR via `create_pull_request`.

### Step 3: Post Response

Call `add_comment` with a concise response:

1. **Key takeaway**
2. **Evidence**
3. **Actions taken** (including validation results and PR link if created)

${{ inputs.additional-instructions }}
