---
inlined-imports: true
description: "Find small, related issues and open a focused PR"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-issue.md
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
      EXTRA_COMMIT_GITHUB_TOKEN:
        required: false
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-small-problem-fixer
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
  max-patch-size: 10240
  noop:
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Small Problem Fixer

Find a small, clearly-scoped issue (or a very small set of related issues) and open a single focused PR that fixes it.

## Context

- **Repository**: ${{ github.repository }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, create a pull request, add issue comments.
- **CANNOT**: Push directly to the repository — use `create_pull_request`.
- **Only one PR per run.**
- Only combine issues if they share the same root cause and the fix is a single small change (no broad refactors).
- Skip issues that need design decisions, large refactors, or ambiguous reproduction steps.
- If no suitable issue is found or the fix is not safe to implement quickly, call `noop` with a brief reason.
- **Most runs should end with `noop`.** Only open a PR when the fix is clearly correct, tested, and small enough that a reviewer would approve it quickly.

## Step 1: Gather candidates

1. Search for small, low-effort issues:

````text
github-search_issues: query="repo:${{ github.repository }} is:issue is:open -label:bug-hunter -\"[bug-hunter]\" (label:\"good first issue\" OR label:small OR label:\"quick fix\" OR label:\"easy\") sort:updated-asc"
````

3. If that yields no good candidates, broaden to low-comment issues:

````text
github-search_issues: query="repo:${{ github.repository }} is:issue is:open -label:bug-hunter -\"[bug-hunter]\" comments:0..2 sort:updated-asc"
````

4. For each candidate, read the full issue and comments using `issue_read` (methods `get` and `get_comments`).
5. Only keep candidates whose `author_association` is `OWNER`, `MEMBER`, or `COLLABORATOR` (skip all others).

## Step 2: Select a target

Choose:
- **One** best issue; or
- **Up to three** tightly related issues with a shared root cause and a single minimal fix.

Prefer issues that:
- Are clearly actionable with a small code change
- Have short or straightforward reproduction steps
- Have no active discussion indicating complex design work
- Are not duplicate reports of prior Bug Hunter issues (search open + closed Bug Hunter issues for overlap and skip duplicates).

## Step 3: Implement the fix

1. Locate the relevant code via search and file reads.
2. Make the smallest safe change that fixes the issue(s).
3. Determine required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config; run required commands relevant to the change and capture results, even if they are long-running or marked as heavy.
4. Run the most relevant tests (prefer the full relevant suite even if slow). **Tests must pass.** If no tests exist for the area, write a minimal test that validates the fix.
5. Commit the changes locally.

## Step 4: Quality Gate — Self-Review

Before creating the PR, review your own changes critically:

- **Correctness**: Does the fix actually address the issue? Did tests pass?
- **Scope**: Is the change minimal? Would a reviewer question why any line was touched?
- **Safety**: Could this break anything else? If you're unsure, call `noop`.
- **Reviewer experience**: Would a maintainer approve this quickly, or would it need multiple rounds of review?

If the fix feels uncertain, incomplete, or risky, call `noop` with a reason. A skipped run is better than a noisy PR.

## Step 5: Create the PR

Call `create_pull_request` with:
- **Title**: concise fix summary
- **Body**: summary, linked issue(s), required commands/tests run and their results, and any follow-ups
- **Labels**: include `small-problem-fixer` if the label exists (check with `github-get_label`); otherwise omit labels

## Step 6: Close the loop

After creating the PR, add a brief comment on each issue linking to the PR.
If no suitable issue is found, call `noop` with a brief reason.

${{ inputs.additional-instructions }}
