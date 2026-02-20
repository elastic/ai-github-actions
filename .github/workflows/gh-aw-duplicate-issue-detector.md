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
    - "github-actions[bot]"
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
timeout-minutes: 15
safe-outputs:
  noop:
  add-comment:
    max: 1
---

# Duplicate Issue Detector

Check whether newly opened issue #${{ github.event.issue.number }} in ${{ github.repository }} is a duplicate of an existing open or previously closed/resolved issue. Do **not** triage or make an action plan — only determine whether a duplicate exists.

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

A duplicate must describe **the same underlying problem or request**, not merely the same topic area. Ask:
- Does the candidate report the same bug, error, or request the same feature?
- Are the affected component, behavior, and scope the same?

**Do not mark as duplicate if:**
- The candidate covers only a related but distinct problem
- The candidate is closed as "wont fix" or "invalid" with no resolution of the underlying issue
- You are uncertain — only flag clear duplicates

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

**If no duplicate is found:**

Call `noop` with message "No duplicate found for issue #${{ github.event.issue.number }}".

${{ inputs.additional-instructions }}
