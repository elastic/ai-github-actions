---
inlined-imports: true
description: "Check for new ai-github-actions releases and open PRs to update pinned workflow SHAs"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-pr.md
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
  group: release-update
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
strict: false
safe-outputs:
  noop:
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Release Update Check

Check for new releases of `elastic/ai-github-actions` and open a PR that updates pinned workflow SHAs in this repository.

## Context

- **Repository**: ${{ github.repository }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, create a pull request.
- **CANNOT**: Push directly to the repository — use `create_pull_request`.
- **Only one PR per run.**
- Only update workflow references to `elastic/ai-github-actions/.github/workflows/gh-aw-*.lock.yml@...`.
- If no updates are needed, call `noop` with a brief reason.

## Step 1: Gather context

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Use `github-get_latest_release` for `elastic/ai-github-actions` to obtain the latest tag and release notes. If no release exists, call `noop` and stop.
3. Resolve the tag to a commit SHA using `github-get_tag`.
4. Find pinned workflow references in this repository:

````text
rg -n "elastic/ai-github-actions/.github/workflows/gh-aw-.*\\.lock\\.yml@\\S+" .
````

5. Extract the current refs and identify which ones are full commit SHAs. If no references are found, call `noop`.
6. Check for an existing open PR that already targets the latest tag (use `github-search_pull_requests`). If one exists, call `noop`.

## Step 2: Update workflow references

- For each outdated reference, update the ref to the latest release commit SHA.
- Preserve any trailing comments; if a comment exists for the old tag, update it to the latest tag. If no comment exists, add `# <latest tag>` after the ref.
- Do not touch references that already use the latest release SHA or tag.

## Step 3: Suggest workflow improvements

- Review the latest release notes and identify any changes that affect workflow usage or configuration.
- Add a short "Suggested workflow updates" section in the PR body. If there are no relevant suggestions, state that explicitly.

## Step 4: Create the PR

1. Commit the changes locally.
2. Call `create_pull_request` with:
   - **Title**: `Update ai-github-actions workflows to <latest tag>`
   - **Body**: Summary of updated refs (old → new), release note highlights that matter, suggested workflow updates, and tests run (if none, say "Not run (workflow reference updates only)").

${{ inputs.additional-instructions }}
