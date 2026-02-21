---
inlined-imports: true
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
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-duplicate-issue-detector-${{ github.event.issue.number }}"
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
      allowed-bot-users:
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot],copilot"
      detect-related-issues:
        description: "Detect highly related (but not duplicate) issues in addition to exact duplicates (default: true)"
        type: string
        required: false
        default: "true"
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

**Related issues detection setting**: ${{ inputs.detect-related-issues }}

Classify each promising candidate using the categories below. If related issues detection is disabled (setting is `"false"`), only use the **Clear duplicate** and **Not related** categories — skip the **Highly related** category entirely.

**Clear duplicate** — the candidate describes **the same underlying problem or request**:
- Reports the same bug or requests the exact same feature
- The affected component, behavior, and scope are the same
- A fix for the candidate would fully resolve this issue too

**Highly related** *(only when related issues detection is enabled)* — the candidate is closely related but **not** the same issue:
- Covers a very similar area, component, or failure mode
- One issue is a subset or superset of the other
- Both issues overlap significantly but each has distinct scope or nuance

**Not related** — skip it if:
- The candidate only shares the same general topic area
- The candidate is closed as "wont fix" or "invalid" with no resolution of the underlying issue
- You are uncertain — when in doubt, err on the side of "not related"; if related issues detection is enabled, prefer "highly related" over "duplicate" for borderline overlapping cases

### Step 4: Post Result

Post **exactly one** `add_comment` call total (or `noop` if nothing is found). Do not call `add_comment` more than once.

**If any duplicates (or highly related issues, when detection is enabled) were found:**

Call `add_comment` with a single comment combining all findings. Include up to **3 duplicate issues** and, when related issues detection is enabled, up to **3 highly related issues**, each ranked from most to least relevant to the current issue. Use this format:

```
**Possible duplicates** (issues that appear to describe the same problem):
- #{number} — {one concise sentence explaining why this issue overlaps with the candidate issue}
  <details><summary>More detail</summary>
  {optional extra context about shared symptoms, component, or scope}
  </details>
- #{number} — {one concise sentence explaining why this issue overlaps with the candidate issue}
  <details><summary>More detail</summary>
  {optional extra context about shared symptoms, component, or scope}
  </details>

**Highly related** (separate issues that significantly overlap or share scope):
- #{number} — {one concise sentence explaining the shared scope and the key difference from this issue}
  <details><summary>More detail</summary>
  {optional extra context about the overlap and distinction}
  </details>
- #{number} — {one concise sentence explaining the shared scope and the key difference from this issue}
  <details><summary>More detail</summary>
  {optional extra context about the overlap and distinction}
  </details>
```

Omit the **Highly related** section entirely when related issues detection is disabled or when no issues qualify for it. Omit a section entirely if no issues qualify for it. Put issue references on the main list line (outside `<summary>`) so GitHub renders issue status badges. Keep `<summary>` text generic (for example, `More detail`) and avoid repeating issue titles there. In justifications, refer to the current report as **"this issue"** (not by number). Use neutral, helpful language — the reporter may not be familiar with the existing issues. Do NOT use `fixes`, `closes`, or `resolves` keywords.

**If no duplicate (or highly related issue, when detection is enabled) is found:**

Call `noop` with message "No duplicate found for issue #${{ github.event.issue.number }}".

${{ inputs.additional-instructions }}
