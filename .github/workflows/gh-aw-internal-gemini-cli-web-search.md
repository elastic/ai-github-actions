---
inlined-imports: true
name: "Internal Gemini CLI Web Search"
description: "Gemini-powered web research assistant — investigates issues and posts findings as comments or new issues"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-issue-or-pr.md
  - gh-aw-fragments/safe-output-create-issue.md
engine:
  id: gemini
  model: ${{ inputs.model }}
  env:
    GEMINI_MAX_ATTEMPTS: "10"
  concurrency:
    group: "gh-aw-gemini-${{ github.workflow }}-internal-gemini-cli-web-search-${{ github.event.issue.number }}"
on:
  stale-check: false
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: ""
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
        description: "Allowed bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      title-prefix:
        description: "Title prefix for created issues (e.g. '[research]')"
        type: string
        required: false
        default: "[research]"
    secrets:
      GEMINI_API_KEY:
        required: true
  reaction: "eyes"
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-internal-gemini-cli-web-search-${{ github.event.issue.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: false
  web-fetch:
network:
  firewall: false
safe-outputs:
  activation-comments: false
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-key: "${{ inputs.title-prefix }}"
    close-older-issues: true
    expires: 7d
strict: false
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# Internal Gemini CLI Web Search

Assist with web research on ${{ github.repository }} from issue comments, then provide an evidence-backed answer.

## Context

- **Repository**: ${{ github.repository }}
- **Issue**: #${{ github.event.issue.number }} — ${{ github.event.issue.title }}
- **Request**: "${{ steps.sanitized.outputs.text }}"

## Constraints

- **CAN**: Read files, search code, use web fetch, comment on issues, create issues
- **CANNOT**: Execute commands, modify files, run tests, or push to the repository

## Instructions

Understand the request, investigate repository and external context, and respond with a concise, actionable result.

### Step 1: Gather Context and Plan

1. Read the full issue thread and any referenced issues. Identify the specific question or goal — this is your research anchor for all subsequent steps.
2. Before searching, decompose the question into sub-questions. For complex or multi-faceted requests, list 2–5 specific sub-questions that, if answered, would fully address the original request. This prevents unfocused searching and ensures complete coverage.
3. Use `search_code` and local file reads only when codebase knowledge is needed to answer the question or prepare an implementation.

### Step 2: Research Iteratively

1. Use web fetch as your primary external research method. For each sub-question from Step 1, fetch authoritative sources directly.
2. After each round of searches, assess what you've learned and what gaps remain. If key sub-questions are still unanswered, search again with refined queries — do not settle for incomplete evidence on important points.
3. For any key factual claim, seek at least two independent sources. If only one source exists, note this. If sources conflict, investigate further before drawing conclusions — do not present a claim as settled when the evidence is mixed.
4. Favor primary sources (official documentation, release notes, RFCs, peer-reviewed papers, author blog posts) over secondary summaries or aggregator content. If a claim relies solely on a secondary source, note this.
5. Before moving to synthesis, re-read your findings against the original research anchor from Step 1. Drop any findings that don't help answer the original question — tangential information dilutes the response.

### Step 3: Verify Before Posting

Before writing the response, apply Chain-of-Verification to your draft findings:

1. For each key claim, generate a specific verification question (e.g., "Is it true that X supports Y as of version Z?"). Answer each verification question using the evidence you gathered — if the evidence doesn't clearly support the claim, either search for confirmation or drop the claim.
2. If you hedged with "might," "could," or "possibly," the claim is not ready — either confirm it or drop it.
3. If the research scope was too large to fully investigate, say so explicitly rather than presenting partial findings as complete.

### Step 4: Post Response

Choose the right output:

- **`add_comment`** — use this when responding directly to the research request on the triggering issue. This is the default.
- **`create_issue`** — use this when your findings reveal a distinct problem, action item, or recommendation that deserves its own tracking issue separate from the original request.

Structure your response:

1. **Key takeaway** — lead with the direct answer to the original question
2. **Evidence** — cite specific URLs, docs, or file paths for each claim
3. **Actions taken** (including validation results)
4. **Open questions** — if anything could not be confirmed or conflicting evidence was found, list it here rather than omitting silently

${{ inputs.additional-instructions }}
