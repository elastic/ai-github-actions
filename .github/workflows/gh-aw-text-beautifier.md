---
name: "Text Beautifier"
description: "Find typos, unclear error messages, and awkward user-facing text, then file an improvement issue"
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
  group: text-beautifier
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, labels]
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
    title-prefix: "[text-beautifier] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Find typos, unclear error messages, and awkward user-facing text that are low-effort to fix, and file a single improvement issue.

**The bar is high: only report concrete, unambiguous text problems.** Most runs should end with `noop` — that means user-facing text is clean.

### Data Gathering

1. Call `generate_agents_md` to get repository conventions. If it fails, continue.
2. Identify user-facing text sources — scan the repository for:
   - CLI output strings, error messages, and help text
   - Log messages shown to users (not debug-level internal logs)
   - README, CONTRIBUTING, DEVELOPING, and other markdown documentation
   - UI strings, notification templates, and user-visible configuration descriptions
   - Code comments in public APIs that appear in generated documentation
3. Read the identified files and search for text issues.

### What to Look For

Focus on **concrete, unambiguous problems** in user-facing text:

1. **Typos and misspellings** — real spelling errors, not style preferences (e.g., `recieve` → `receive`, `occurence` → `occurrence`)
2. **Grammatical errors** — subject-verb disagreement, missing articles, broken sentences
3. **Unclear error messages** — errors that do not tell the user what went wrong or what to do next (e.g., `"Error: failed"` with no context)
4. **Inconsistent terminology** — the same concept referred to by different names in different places (e.g., `workspace` vs `project` vs `repo` for the same thing)
5. **Broken or incomplete sentences** — truncated messages, dangling phrases, copy-paste artifacts
6. **Misleading text** — messages that describe behavior that no longer matches the code

### What to Skip

- **Style preferences** — do not flag Oxford comma usage, line length, or prose style unless it causes ambiguity
- **Internal-only text** — debug logs, developer-only comments, test fixtures
- **Intentional abbreviations** — short forms that are standard in the project
- **Generated or vendored files** — do not scan auto-generated code, lock files, or third-party content
- **Issues already tracked** — check open issues before filing
- **Findings that require design decisions** — if fixing the text requires deciding on new terminology or restructuring content, skip it

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- No concrete text problems were found
- All findings are style preferences rather than clear errors
- The problems found are in generated or vendored files
- A similar issue is already open
- The fixes would require design decisions or significant rewording beyond simple corrections

### Issue Format

**Issue title:** Brief summary of text improvements found

**Issue body:**

> ## Text Improvements
>
> The following user-facing text issues were found in the repository. Each is a low-effort fix.
>
> ### 1. [Brief description]
>
> **File:** `path/to/file` (line N)
> **Current text:** `the existing text with the problem`
> **Suggested fix:** `the corrected text`
> **Why:** [Brief explanation — typo, grammar, unclear error, etc.]
>
> ### 2. [Next finding...]
>
> ## Suggested Actions
>
> - [ ] [Specific, actionable checkbox for each fix]

### Labeling

- If the `text-beautifier` label exists (check with `github-get_label`), include it in the `create_issue` call; otherwise, rely on the `[text-beautifier]` title prefix only.

${{ inputs.additional-instructions }}
