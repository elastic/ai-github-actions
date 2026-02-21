---
description: "Find typos, spelling errors, and unclear user-facing text and file a report"
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
    title-prefix: "[text-beautifier] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Find typos, spelling errors, and poor-quality user-facing text across the repository and report the most valuable improvements.

**The bar is actionable and low-risk.** Only report text-only changes — no logic, no structure. Most runs should end with `noop` if the text quality is already good.

### Data Gathering

1. Identify user-facing text surfaces in the repository. Focus on:
   - **Error messages** — strings passed to error constructors, `fmt.Errorf`, `raise`, `throw`, `console.error`, or similar in the primary language.
   - **CLI help text** — `--help` flag descriptions, command descriptions, usage strings, argument documentation.
   - **Log messages** — strings passed to loggers at any level (`log.Info`, `logger.warn`, `logging.error`, etc.).
   - **User-visible output** — `print`, `fmt.Println`, `console.log`, `puts`, and similar output statements that reach end users.
   - **Documentation strings** — inline docstrings, JSDoc comments, rustdoc comments, Python docstrings, or Go doc comments on exported symbols.

2. For each surface, look for:
   - **Typos and misspellings** — words that are clearly misspelled (e.g., `occured` → `occurred`, `recieve` → `receive`, `seperate` → `separate`).
   - **Grammatical errors** — subject–verb disagreement, missing articles, incorrect tense, run-on sentences in messages that will be read by users.
   - **Unclear or unhelpful error messages** — messages like `"error"`, `"failed"`, `"something went wrong"` that give no actionable context. Good error messages say *what* failed, *why*, and (when possible) *how to fix it*.
   - **Inconsistent capitalization** — mixing title case and sentence case for the same type of message within the same file or module.
   - **Truncated or incomplete sentences** — messages that trail off mid-sentence or are obviously unfinished.

3. Check for open issues with the `[text-beautifier]` title prefix to avoid duplicating already-tracked findings.

### What Qualifies as a Finding

Only report an item if **all** of these are true:

1. **Text-only change** — fixing the finding requires changing only a string literal or comment. No logic, no refactoring.
2. **Clear improvement** — the fix is unambiguous. A spelling correction is unambiguous. A stylistic preference is not.
3. **User-facing** — the text is visible to end users (in output, error messages, help text, or public API documentation). Internal comments and variable names are out of scope.
4. **Not already tracked** — no open issue or PR already addresses this exact finding.

### What to Skip

- Internal variable names, function names, or private comments — not user-facing.
- Stylistic preferences where reasonable people disagree (Oxford comma, British vs. American spelling in a mixed codebase).
- Auto-generated files, vendored dependencies, or lock files.
- Test fixtures or test assertion strings — these are internal.
- Changes that would require logic modifications alongside the text fix.

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- You found no findings that pass all four criteria above.
- Every candidate requires judgment calls about style rather than clear correctness.
- The only findings are in internal code (tests, vendor, generated files).
- A recent `[text-beautifier]` issue already covers the same findings.

**Noop is the expected outcome most runs.** A clean codebase with good text quality is a success.

### Issue Format

**Issue title:** Text quality findings — [count] improvements identified

**Issue body:**

> ## Text Quality Report
>
> The following user-facing text issues were found. All are text-only changes — no logic modification needed.
>
> ### 1. [File path, line range] — [Brief description]
>
> **Current:** `[exact current text]`
> **Suggested:** `[suggested replacement]`
> **Reason:** [Why this is a clear improvement]
>
> ### 2. ...
>
> ## Suggested Actions
>
> - [ ] Fix `[brief description]` in `[file]`
> - [ ] ...

**Guidelines:**
- Group findings by file when there are multiple issues in the same file.
- Include exact line numbers or ranges so a maintainer can find the text immediately.
- Keep suggested replacements conservative — prefer the minimal fix over a full rewrite.
- Cap the report at 15 findings per run. Prefer the most impactful (typos in error messages > capitalization in log messages).
- If no findings qualify, call `noop` with: "No text quality issues found — reviewed [surface count] user-facing text surfaces"

${{ inputs.additional-instructions }}
