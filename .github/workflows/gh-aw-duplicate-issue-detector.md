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
    group: "gh-aw-copilot-${{ github.workflow }}-duplicate-issue-detector-${{ github.event.issue.number }}"
on:
  stale-check: false
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
        description: "Allowed bot actor usernames (comma-separated)"
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
  group: ${{ github.workflow }}-duplicate-issue-detector-${{ github.event.issue.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
strict: false
timeout-minutes: 30
safe-outputs:
  activation-comments: false
  noop:
    report-as-issue: false
steps:
  - name: Prescan issue index
    env:
      GH_TOKEN: ${{ github.token }}
    run: |
      set -euo pipefail
      mkdir -p /tmp/gh-aw/agent

      issues_file="/tmp/gh-aw/agent/issues-index.tsv"
      printf "number\ttitle\tstate\n" > "$issues_file"

      # Newest 500 issues (most likely to match recent duplicates)
      gh search issues --repo "$GITHUB_REPOSITORY" --sort created --order desc --limit 500 --json number,title,state \
        --jq '.[] | [.number, .title, .state] | @tsv' >> "$issues_file" || { echo "::warning::Failed to fetch newest issues"; }

      # Oldest 500 issues (covers long-standing items)
      gh search issues --repo "$GITHUB_REPOSITORY" --sort created --order asc --limit 500 --json number,title,state \
        --jq '.[] | [.number, .title, .state] | @tsv' >> "$issues_file" || { echo "::warning::Failed to fetch oldest issues"; }

      # Deduplicate (newest and oldest may overlap for repos with <1000 issues)
      awk -F'\t' '!seen[$1]++' "$issues_file" > "${issues_file}.tmp" && mv "${issues_file}.tmp" "$issues_file"

      count="$(tail -n +2 "$issues_file" | wc -l | tr -d ' ')"
      echo "Prescanned ${count} issues into ${issues_file}"
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

### Step 2: Scan the Issue Index

A prescan step has already fetched issue numbers, titles, and states into `/tmp/gh-aw/agent/issues-index.tsv`. Start by reading this file:

```
cat /tmp/gh-aw/agent/issues-index.tsv
```

Scan the titles for obvious matches against the key terms you identified in Step 1. Note any promising candidate issue numbers — you will verify them in the next step.

### Step 3: Search for Duplicates

Run several targeted searches to complement the index scan. Search **both open and closed** issues.

Suggested queries (adapt based on the issue content):
```
repo:${{ github.repository }} is:issue "{key term from title}"
repo:${{ github.repository }} is:issue is:closed "{key term from title}"
repo:${{ github.repository }} is:issue "{error message or identifier}"
```

For each candidate result (from the index scan or from search), read the title and (if promising) the body to assess similarity.

### Step 4: Evaluate Candidates

**Related issues detection setting**: ${{ inputs.detect-related-issues }}

Classify each promising candidate into one of the categories below. If related issues detection is disabled (setting is `"false"`), skip the **Related** category entirely.

**Duplicate** — a fix or resolution for the candidate would **fully resolve this issue too**:
- Reports the same bug with the same root cause, or requests the exact same feature
- The affected component, behavior, and scope match
- One being closed as "done" means the other is also done
- Closed historical issues can still be useful context, but if this report has credible evidence of recurrence/regression after closure (for example newer branch/version, fresh failing runs, or changed failure characteristics), prefer **Related** unless sameness is clear
- Be especially cautious when issue comments/timeline indicate the earlier issue was actually resolved; treat that as a signal to prefer **Related** unless there is strong evidence this is still the same unresolved problem

**Related** *(only when detection is enabled)* — **not** the same issue, but may provide useful context or a partial answer:
- Covers a similar area, component, or failure mode but has distinct scope
- Contains discussion, workarounds, or decisions that would help the reporter
- One issue is a subset or superset of the other

**Skip** a candidate if:
- It only shares the same general topic area
- It is closed as "won't fix" or "invalid" with no useful discussion
- You are uncertain — when in doubt, skip it; prefer **Related** over **Duplicate** for borderline cases

### Evaluation Rubric (Required)

Before posting your result, evaluate your best candidate(s) against this rubric:

1. **Similarity evidence** — component/failure signature/scope clearly match this issue
2. **Recurrence handling** — recurrence/regression signals are handled conservatively (prefer **Related** when uncertain)
3. **Closure safety** — "safe to close" is used only with high confidence
4. **Maintainer utility** — explanation helps a maintainer act quickly without re-investigating from scratch

Use this rubric as a hard gate:
- If fewer than **3/4** criteria are satisfied, do not classify as **Duplicate**.
- If confidence is mixed, prefer **Related** (or skip/noop if nothing useful remains).

### Step 5: Post Result

Post **exactly one** `add_comment` call (or `noop` if nothing is found). Do not call `add_comment` more than once.

**If any duplicates or related issues were found:**

Call `add_comment` with a single comment. Include up to **3 duplicates** and up to **3 related issues**, ranked most-to-least relevant.

When there are duplicates, start with a recommendation line telling the maintainer whether this issue looks safe to close — for example: *"This issue looks like a duplicate of #123 and may be safe to close."* If there are multiple duplicate candidates, recommend the single best one.
Use this "safe to close" recommendation only when confidence is high that the candidate fully covers this issue now; if there are plausible recurrence/regression signals, skip the closure recommendation and present the candidate(s) as context.

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
