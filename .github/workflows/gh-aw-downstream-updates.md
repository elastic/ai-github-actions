---
description: "Check downstream repositories for workflow configuration drift and recommend updates"
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
  group: downstream-updates
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

# Report Assignment

Check downstream repositories in the `elastic` and `strawgate` orgs for workflow configuration drift relative to the latest best practices and examples from `elastic/ai-github-actions`.

## Data Gathering

### Step 1: Understand the current best practices

1. Read `data/downstream-users.json` from this repository to get the current list of downstream repositories and which workflows they use.

2. Read the latest release from `elastic/ai-github-actions` using `github-list_releases` (owner: `elastic`, repo: `ai-github-actions`, perPage: 5) to understand what changed recently. Note the most recent release tag.

3. For each distinct workflow name appearing in any downstream repo's `workflows` list, fetch the canonical `example.yml` from this repository. For example, for workflow `workflows/pr-review/rwx`, fetch `gh-agent-workflows/pr-review/example.yml` from `elastic/ai-github-actions`. This is the reference configuration consumers should be using.

   Use `github-get_file_contents` with owner: `elastic`, repo: `ai-github-actions`, path: `gh-agent-workflows/<name>/example.yml` (where `<name>` is the workflow slug, e.g. `pr-review`, `mention-in-issue`). Also fetch the corresponding `README.md` at `gh-agent-workflows/<name>/README.md` to understand required permissions, inputs, and safe-output notes.

4. Read `RELEASE.md` from `elastic/ai-github-actions` to understand the release conventions and any upgrade guidance.

### Step 2: Inspect each downstream repository

For each repository listed in `data/downstream-users.json`:

1. Search for workflow files that reference `elastic/ai-github-actions`:
   - Use `github-search_code` with query: `repo:{owner}/{repo} elastic/ai-github-actions language:yaml`
   - For each matching file, fetch its full content with `github-get_file_contents`.

2. Parse each workflow file to extract:
   - The `uses:` reference (e.g., `elastic/ai-github-actions/.github/workflows/gh-aw-pr-review.lock.yml@v0`)
   - The pinned version tag (e.g., `@v0`, `@v0.44.0`, or a SHA)
   - Declared `permissions:` at the job or workflow level
   - Declared `on:` triggers (schedule cron, events, workflow_dispatch)
   - Any `with:` inputs passed to the workflow
   - The `secrets:` block

## What to Look For

For each downstream workflow file, compare it against the canonical `example.yml` and `README.md`. Flag these categories of drift:

### 1. Missing or incorrect permissions

Each workflow's README lists the permissions it requires. Common required permissions:
- `issues: write` — needed for workflows that create or comment on issues
- `pull-requests: write` — needed for workflows that comment on or review PRs
- `contents: write` — needed for workflows that push changes

Flag any workflow that is **missing** a required permission, or that has **no** `permissions:` block at all when the canonical example specifies one.

### 2. Outdated version pin

The canonical `example.yml` uses `@v0` (floating major tag). Flag:
- Workflows pinned to an older floating tag (e.g., `@v0` is correct; a SHA or a specific version like `@v0.44.0` may be outdated)
- Workflows not using the `@v0` floating tag convention

### 3. Missing `workflow_dispatch` trigger

The canonical examples include `workflow_dispatch` for manual runs. Flag any workflow that has a `schedule:` trigger but no `workflow_dispatch:` trigger.

### 4. Missing required secrets

All `gh-aw-*.lock.yml` workflows require `COPILOT_GITHUB_TOKEN`. Flag if the calling workflow does not pass this secret.

### 5. Misconfigured schedule

Compare the cron schedule in the downstream workflow against the canonical example. Flag schedules that differ significantly (e.g., running hourly when the canonical suggests daily, or missing a schedule entirely for a workflow that should run on a schedule).

### 6. Workflows the repo should consider adding

Based on the workflows this repo uses, identify any from the canonical list (in `gh-agent-workflows/`) that would be a natural fit for the downstream repo but are not yet installed. Only flag well-established workflows (not experimental ones). Limit to a maximum of 3 suggestions per repo.

## What to Skip

- Repos that are already up-to-date with no drift
- Minor stylistic differences (e.g., comment formatting, extra blank lines)
- Workflows pinned with SHAs from a repo that explicitly manages its own pin updates via `release-update`
- Repos where only a `noop` trigger is present (no real drift)

## Issue Format

**Issue title:** Downstream updates needed — [date]

**Issue body:**

> ## Downstream Workflow Update Report
>
> This report identifies configuration drift between downstream workflow installations and the current `elastic/ai-github-actions` best practices.
>
> **Latest release:** [tag] — [date]
>
> ---
>
> ### [owner/repo]
>
> #### Workflow: `[workflow-file-path]` (`[uses: reference]`)
>
> | Check | Status | Details |
> | --- | --- | --- |
> | Permissions | ⚠️ Missing `issues: write` | Required by this workflow |
> | Version pin | ✅ Using `@v0` | — |
> | `workflow_dispatch` | ⚠️ Missing | Add `workflow_dispatch:` to enable manual runs |
> | `COPILOT_GITHUB_TOKEN` secret | ✅ Present | — |
>
> **Suggested fix:** [Short description of what to change and a link to the canonical example]
>
> #### Additional workflows to consider
>
> - [`mention-in-issue`](https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-issue/example.yml) — Responds to `/ai` mentions in issues
>
> ---
>
> ### [next repo...]
>
> ---
>
> ## Summary
>
> | Repository | Issues found |
> | --- | --- |
> | owner/repo | 2 |
> | ... | ... |
>
> **Total repositories checked:** [count]
> **Repositories with drift:** [count]
> **Total issues found:** [count]
>
> ## Suggested Actions
>
> - [ ] [owner/repo]: Add `issues: write` permission to `[file]`
> - [ ] [owner/repo]: Add `workflow_dispatch:` trigger to `[file]`

**Guidelines:**
- One section per downstream repository
- Within each section, one subsection per affected workflow file
- Use the table format shown above for each workflow — check marks and warning signs make it easy to scan
- Include direct links to the downstream workflow file and the canonical `example.yml` for each item flagged
- If a repository has no drift, omit it from the report
- If no repositories have any drift, call `noop` with: "All downstream workflow configurations are up to date."

${{ inputs.additional-instructions }}
