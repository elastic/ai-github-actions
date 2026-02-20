---
description: "Track downstream public repo usage of elastic/ai-github-actions and update data"
timeout-minutes: 60
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-pr.md
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
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: downstream-users
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
roles: [admin, maintainer, write]
safe-outputs:
  noop:
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Downstream Users Tracking

Maintain a canonical list of public downstream repositories using elastic/ai-github-actions, including which workflows they consume.

## Context

- **Repository**: ${{ github.repository }}
- **Output file**: `data/downstream-users.json`

## Constraints

- **CAN**: Read files, search GitHub, modify files locally, run commands, create a pull request.
- **CANNOT**: Directly push to the repository — use `create_pull_request`.
- **Only one PR per run.**
- Do not modify files under `.github/workflows/`.
- Keep the JSON output stable and sorted to minimize diff noise.

## Step 1: Gather Context

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Read the current `data/downstream-users.json` file (if it exists).

## Step 2: Discover Downstream Usage

1. Use the `public-code-search` MCP server to find public repositories that reference this repo in workflow files.
   - Search for `uses: elastic/ai-github-actions` in `*.yml` and `*.yaml` files.
   - Example query input for `search_code`:
     - `patterns`: `uses:\\s*elastic/ai-github-actions/`
     - `include_globs`: `**/*.yml`, `**/*.yaml`
   - Exclude `elastic/ai-github-actions` itself.

2. For each unique repo + path pair returned:
   - Fetch the workflow file using `github-get_file_contents`.
   - Extract every `uses: elastic/ai-github-actions/...` line.
   - Normalize each entry by removing the leading `elastic/ai-github-actions/` and any `@version` suffix.

## Step 3: Build the Data File

Write `data/downstream-users.json` with this structure:

````markdown
```json
{
  "generated_at": "<ISO-8601 UTC timestamp>",
  "source": {
    "query": "<search query summary>",
    "notes": "<short note about how results were collected>"
  },
  "repos": [
    {
      "repo": "owner/repo",
      "workflows": ["workflows/mention-in-issue/rwxp", "..."]
    }
  ]
}
```
````

Guidelines:
- Sort `repos` by `repo`.
- Sort each `workflows` list alphabetically.
- Use UTC timestamps with a `Z` suffix.

## Step 4: Create the PR

1. If the file is unchanged, call `noop` with: `Downstream users list already up to date.`
2. Otherwise, commit the updated JSON and call `create_pull_request`.
   - Title: `"[downstream] Update downstream users list"`
   - Body:
     - Summary of repo count and workflow count
     - The search query used
     - Any exclusions (self repo, archived/forks if excluded)

${{ inputs.additional-instructions }}
