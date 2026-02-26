---
inlined-imports: true
name: "Text Auditor"
description: "Find typos, unclear error messages, and awkward user-facing text, then file an improvement issue"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/best-of-three-investigation.md
  - gh-aw-fragments/scheduled-audit.md
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
      edit-typos:
        description: "How aggressively to flag typos and misspellings. 'high' = suggest broad consistency fixes, 'low' = flag only clear spelling errors, 'none' = skip typo checks"
        type: string
        required: false
        default: "low"
      edit-grammar:
        description: "How aggressively to flag grammar and sentence construction problems. 'high' = improve awkward sentence structure, 'low' = flag only clear grammatical errors, 'none' = skip grammar checks"
        type: string
        required: false
        default: "low"
      edit-clarity:
        description: "How aggressively to flag unclear user-facing text, especially error/help messages. 'high' = proactively suggest clearer phrasing, 'low' = flag only clearly ambiguous text, 'none' = skip clarity checks"
        type: string
        required: false
        default: "low"
      edit-terminology:
        description: "How aggressively to flag inconsistent terminology for the same concept. 'high' = proactively normalize wording, 'low' = flag only unambiguous inconsistencies, 'none' = skip terminology checks"
        type: string
        required: false
        default: "low"
      edit-misleading-text:
        description: "How aggressively to flag text that conflicts with current behavior. 'high' = proactively flag likely drift, 'low' = flag only direct contradictions, 'none' = skip behavior-alignment checks"
        type: string
        required: false
        default: "low"
      title-prefix:
        description: "Title prefix for created issues (e.g. '[text-auditor]')"
        type: string
        required: false
        default: "[text-auditor]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: text-auditor
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
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-issues: false
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

## Edit Level Configuration

The following edit levels are configured for this run. Each dimension is independent.

| Dimension | Level | Meaning |
| --- | --- | --- |
| **typos** | `${{ inputs.edit-typos }}` | How aggressively to flag typos and misspellings |
| **grammar** | `${{ inputs.edit-grammar }}` | How aggressively to flag grammar and sentence construction issues |
| **clarity** | `${{ inputs.edit-clarity }}` | How aggressively to flag unclear user-facing text |
| **terminology** | `${{ inputs.edit-terminology }}` | How aggressively to flag inconsistent naming for the same concept |
| **misleading-text** | `${{ inputs.edit-misleading-text }}` | How aggressively to flag text that no longer matches behavior |

Level semantics:
- **`high`** — apply best judgment proactively within this dimension
- **`low`** — report only concrete, unambiguous issues
- **`none`** — skip this dimension entirely

### Data Gathering

1. Identify user-facing text sources — scan the repository for:
   - CLI output strings, error messages, and help text
   - Log messages shown to users (not debug-level internal logs)
   - README, CONTRIBUTING, DEVELOPING, and other markdown documentation
   - UI strings, notification templates, and user-visible configuration descriptions
   - Code comments in public APIs that appear in generated documentation
2. Read the identified files and search for text issues.

### What to Look For by Dimension

Use each dimension's configured level to determine whether to report findings.

#### Typos (`${{ inputs.edit-typos }}`)

- **`high`**: Flag typos/misspellings proactively and include nearby consistency fixes when they are obviously beneficial.
- **`low`**: Flag only clear spelling errors (for example, `recieve` → `receive`), not style variants.
- **`none`**: Skip typo checks.

#### Grammar (`${{ inputs.edit-grammar }}`)

- **`high`**: Flag grammar and sentence construction issues that reduce readability, including awkward or fragmented sentences.
- **`low`**: Flag only clear grammatical errors (subject-verb disagreement, missing articles, broken sentence structure).
- **`none`**: Skip grammar checks.

#### Clarity (`${{ inputs.edit-clarity }}`)

- **`high`**: Proactively flag unclear user-facing text and suggest concrete rewrites, especially for errors/help text.
- **`low`**: Flag only clearly ambiguous or incomplete user-facing text (for example, `"Error: failed"` with no actionable context).
- **`none`**: Skip clarity checks.

#### Terminology (`${{ inputs.edit-terminology }}`)

- **`high`**: Proactively flag inconsistent naming for the same concept across user-facing surfaces.
- **`low`**: Flag only unambiguous inconsistencies where the same concept is clearly referred to by different terms.
- **`none`**: Skip terminology checks.

#### Misleading Text (`${{ inputs.edit-misleading-text }}`)

- **`high`**: Proactively flag text likely to have drifted from behavior.
- **`low`**: Flag only direct, verifiable contradictions between text and current code behavior.
- **`none`**: Skip behavior-alignment checks.

### What to Skip

- **Style preferences** — do not flag Oxford comma usage, line length, or prose style unless it causes ambiguity
- **Internal-only text** — debug logs, developer-only comments, test fixtures
- **Intentional abbreviations** — short forms that are standard in the project
- **Generated or vendored files** — do not scan auto-generated code, lock files, or third-party content
- **Issues already tracked** — check open issues before filing
- **Findings that require design decisions** — if fixing the text requires deciding on new terminology or restructuring content, skip it

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- All edit dimensions are set to `none`
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

- If the `text-auditor` label exists (check with `github-get_label`), include it in the `create_issue` call; otherwise, rely on the `${{ inputs.title-prefix }}` title prefix only.

${{ inputs.additional-instructions }}
