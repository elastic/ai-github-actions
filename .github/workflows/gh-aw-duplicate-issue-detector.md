---
inlined-imports: true
description: "Detect duplicate issues and notify reporters when a matching open or closed issue exists"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-issue.md
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
        default: "github-actions[bot]"
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
  activation-comments: false
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
repo:${{ github.repository }} is:issue "{key term from title}"
repo:${{ github.repository }} is:issue is:closed "{key term from title}"
repo:${{ github.repository }} is:issue "{error message or identifier}"
```

For each candidate result, read the title and (if promising) the body to assess similarity.

### Step 3: Evaluate Candidates

**Related issues detection setting**: ${{ inputs.detect-related-issues }}

Classify each promising candidate into one of the categories below. If related issues detection is disabled (setting is `"false"`), skip the **Related** category entirely.

**Duplicate** — a fix or resolution for the candidate would **fully resolve this issue too**:
- Reports the same bug with the same root cause, or requests the exact same feature
- The affected component, behavior, and scope match
- One being closed as "done" means the other is also done

**Related** *(only when detection is enabled)* — **not** the same issue, but may provide useful context or a partial answer:
- Covers a similar area, component, or failure mode but has distinct scope
- Contains discussion, workarounds, or decisions that would help the reporter
- One issue is a subset or superset of the other

**Skip** a candidate if:
- It only shares the same general topic area
- It is closed as "won't fix" or "invalid" with no useful discussion
- You are uncertain — when in doubt, skip it; prefer **Related** over **Duplicate** for borderline cases

### Step 4: Post Result

Post **exactly one** `add_comment` call (or `noop` if nothing is found). Do not call `add_comment` more than once.

**If any duplicates or related issues were found:**

Call `add_comment` with a single comment. Include up to **3 duplicates** and up to **3 related issues**, ranked most-to-least relevant.

When there are duplicates, start with a recommendation line telling the maintainer whether this issue looks safe to close — for example: *"This issue looks like a duplicate of #123 and may be safe to close."* If there are multiple duplicate candidates, recommend the single best one.

Example with both duplicates and related issues:

```
This issue looks like a duplicate of #101 and may be safe to close.

**Possible duplicates:**
- #101 — {why this is the same problem, e.g. "same crash in the auth module when tokens expire"}
- #88 — {why this is the same problem}

<details><summary>{N} related issues</summary>

- #204 — {how this could help, e.g. "documents a workaround for the same timeout behavior"}
- #190 — {how this could help}

</details>
```

Example with only duplicates:

```
This issue looks like a duplicate of #101 and may be safe to close.

**Possible duplicates:**
- #101 — {why this is the same problem}
```

Example with only related issues:

```
<details><summary>{N} related issues</summary>

- #204 — {how this could help}
- #190 — {how this could help}

</details>
```

Formatting rules:
- Put `#{number}` on the list line so GitHub renders status badges
- Do NOT repeat issue titles or numbers in justification text
- Refer to the current report as "this issue" and to candidates by "it" or a short description
- Do NOT use `fixes`, `closes`, or `resolves` keywords (they auto-close issues)
- For duplicates, explain **why it is the same problem**
- For related issues, explain **how it could help the reporter**

**If nothing is found:**

Call `noop` with message "No duplicate found for issue #${{ github.event.issue.number }}".

${{ inputs.additional-instructions }}
