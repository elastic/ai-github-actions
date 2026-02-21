---
description: "Detect duplicate issues and notify reporters when a matching open or closed issue exists"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment.md
engine:
  id: copilot
  model: gpt-5.3-codex
  concurrency:
    group: "gh-aw-copilot-duplicate-issue-detector-${{ github.event.issue.number }}"
on:
  workflow_call:
    inputs:
      additional-instructions:
        description: "Repo-specific instructions appended to the agent prompt"
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
  group: duplicate-issue-detector-${{ github.event.issue.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
strict: false
timeout-minutes: 30
safe-outputs:
  noop:
    report-as-issue: false
  add-comment:
    max: 1
---

# Duplicate Issue Detector

Check whether newly opened issue #${{ github.event.issue.number }} in ${{ github.repository }} is a duplicate of, or highly related to, an existing open or previously closed/resolved issue. Do **not** triage or make an action plan — only determine whether a duplicate or highly related issue exists.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}

## Process

### Step 1: Understand the Issue

Read the issue title and body carefully. Identify:
- The core problem or request (in one sentence)
- Key terms, error messages, component names, or identifiers you can use as search queries

### Step 2: Search for Duplicates

Run several targeted searches. Search **both open and closed** issues.

Suggested queries (adapt based on the issue content):
```
repo:{owner}/{repo} is:issue "{key term from title}"
repo:{owner}/{repo} is:issue is:closed "{key term from title}"
repo:{owner}/{repo} is:issue "{error message or identifier}"
```

For each candidate result, read the title and (if promising) the body to assess similarity.

### Step 3: Evaluate Candidates

Classify each promising candidate into one of three categories:

**Clear duplicate** — the candidate describes **the same underlying problem or request**:
- Reports the same bug or requests the exact same feature
- The affected component, behavior, and scope are the same
- A fix for the candidate would fully resolve this issue too

**Highly related** — the candidate is closely related but **not** the same issue:
- Covers a very similar area, component, or failure mode
- One issue is a subset or superset of the other
- Both issues overlap significantly but each has distinct scope or nuance

**Not related** — skip it if:
- The candidate only shares the same general topic area
- The candidate is closed as "wont fix" or "invalid" with no resolution of the underlying issue
- You are uncertain — when in doubt, prefer "not related" over "highly related", and "highly related" over "duplicate"

### Step 4: Post Result

**If a clear duplicate is found:**

Call `add_comment` with a concise comment in this format:

> This issue appears to be a duplicate of #{number} — {title}.
>
> {One sentence explaining the similarity.}
>
> Linking to the existing issue for tracking. If this is actually a different problem, please add more details to distinguish it.

- Reference at most **one** best-matching duplicate (the most relevant open issue takes priority over a closed one).
- Use neutral, helpful language — the reporter may not be familiar with the existing issue.
- Do NOT use `fixes`, `closes`, or `resolves` keywords.

**If a highly related (but not duplicate) issue is found:**

Call `add_comment` with a concise comment in this format:

> This issue is highly related to #{number} — {title}.
>
> {One sentence explaining how they are related and how they differ.}
>
> Linking for visibility — these are separate issues but may benefit from coordination.

- Reference at most **one** best-matching related issue.
- Use neutral, helpful language — the reporter may not be familiar with the existing issue.
- Do NOT use `fixes`, `closes`, or `resolves` keywords.

**If no duplicate or highly related issue is found:**

Call `noop` with message "No duplicate found for issue #${{ github.event.issue.number }}".

${{ inputs.additional-instructions }}
