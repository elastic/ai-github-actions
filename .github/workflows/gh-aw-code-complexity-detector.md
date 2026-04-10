---
inlined-imports: true
name: "Code Complexity Detector"
description: "Find overly complex code and file a simplification report"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/pick-three-keep-many.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/network-ecosystems.md
  - gh-aw-fragments/code-quality-audit.md
engine:
  id: copilot
  model: ${{ inputs.model }}
on:
  stale-check: false
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      languages:
        description: "Comma-separated languages to analyze (e.g., go,python,typescript). Ignored if file-globs is set."
        type: string
        required: false
        default: "go"
      file-globs:
        description: "Comma-separated file globs to analyze (overrides languages mapping)"
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
      severity-threshold:
        description: "Minimum severity to include in the report. 'high' = only complexity causing active maintenance problems. 'medium' (default) = also include clear simplification opportunities. 'low' = also include minor complexity."
        type: string
        required: false
        default: "medium"
      title-prefix:
        description: "Title prefix for created issues (e.g. '[complexity]')"
        type: string
        required: false
        default: "[complexity]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-code-complexity-detector
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
# Serena MCP (oraios/serena) — symbolic / LSP-backed code tools; stdio via uvx (setup-uv is emitted by the compiler).
mcp-servers:
  serena:
    command: uvx
    args:
      - "-p"
      - "3.13"
      - "--from"
      - "git+https://github.com/oraios/serena"
      - "serena"
      - "start-mcp-server"
      - "--context"
      - "ide"
      - "--project-from-cwd"
      - "--open-web-dashboard"
      - "false"
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-key: "${{ inputs.title-prefix }}"
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

Find overly complex code and file a simplification report.

**Inputs**
- **Languages**: `${{ inputs.languages }}`
- **File globs**: `${{ inputs.file-globs }}`

### Data Gathering

1. Determine file globs and store them as a space-delimited `GLOBS` list:
   - If `file-globs` is set, split it on commas and trim whitespace.
   - Otherwise, map `languages` (comma-separated) to globs using:
     - go → `**/*.go`
     - python → `**/*.py`
     - javascript → `**/*.{js,mjs,cjs}`
     - typescript → `**/*.{ts,tsx}`
     - java → `**/*.java`
     - ruby → `**/*.rb`
     - csharp → `**/*.cs`
     - rust → `**/*.rs`
2. Find all matching files (excluding tests and generated files):
   ```bash
   FILES=$(for glob in ${GLOBS}; do
     rg --files \
       -g "${glob}" \
       -g "!**/*_test.*" \
       -g "!**/test_*" \
       -g "!**/*.spec.*" \
       -g "!**/*.test.*" \
       -g "!**/*.pb.*" \
       -g "!**/*_gen.*" \
       -g "!**/generated/**"
   done | sort -u)
   ```
3. If no files are found, call `noop` with a brief reason and stop.
4. Call Serena `activate_project` with `${{ github.workspace }}`.
5. If there are more than 200 files, focus on the 200 largest by line count:
   ```bash
   printf '%s\n' "$FILES" | xargs wc -l | sort -nr | head -200 | awk '{print $2}'
   ```
6. For each selected file, use `get_symbols_overview` (Serena) when supported; otherwise, extract functions/methods with language-appropriate `rg` patterns and light file inspection.
7. Use the **Pick Three, Keep Many** pattern for the analysis phase: spawn 3 `general-purpose` sub-agents, each searching for complexity from a different angle (e.g., one measuring nesting depth and cyclomatic complexity, one looking for redundant conditionals and style outliers, one checking for inline logic that reimplements existing helpers). Include the file list, symbol inventory, and the full "How to Analyze" / "What to Skip" criteria in each sub-agent prompt. Each sub-agent should return all findings that meet the quality criteria.

### How to Analyze

1. Build an inventory by file and directory of:
   - Module/package/namespace (when applicable)
   - Function and method names (with receivers/classes if relevant)
   - Rough line count per function
2. Identify complexity hotspots:
   - **Deep nesting** (3+ levels of indentation within a function)
   - **Redundant conditionals** (branches that collapse to simpler logic)
   - **Long functions** (>50 lines with multiple responsibilities)
   - **Style outliers** (verbose patterns where the rest of the codebase uses a concise idiom)
   - **Inline reimplementation** (custom logic that duplicates an existing helper or standard library function)
3. Use Serena (`find_symbol`, `search_for_pattern`, `find_referencing_symbols`) when supported to trace helper reuse and identify reimplementations.
4. Focus on high-impact, actionable findings where a simplification is clearly safe and behavior-preserving.

### Bar for Merit

A finding must clear at least one of these bars to be worth reporting:

1. **Style conformance** — the code is a clear outlier compared to the rest of the codebase (e.g., one function uses a verbose pattern that every other function avoids).
2. **Helper reuse** — an existing utility or helper function already does what the code is reimplementing.
3. **Significant clarity improvement** — the change meaningfully reduces complexity (e.g., collapsing 10+ lines of tangled logic into 2–3 readable lines, early returns eliminating deep nesting, extracting a helper from repeated inline logic).

**Do not report** micro-changes that swap one valid idiom for another (renaming variables, reordering equivalent expressions, replacing a two-line pattern with a one-liner). These are not worth a maintainer's time to review.

### What to Skip

- Test or generated files
- Trivial helpers (<5 lines) unless they are style outliers
- Subjective complexity preferences — only flag code that is clearly overcomplicated, not "could be slightly cleaner"
- Functions that are long but straightforward (e.g., switch statements mapping many values)

### Issue Format

**Issue title:** Code complexity findings (date)

**Issue body:**

> ## Summary
> - Files analyzed: [count]
> - Functions cataloged: [count]
> - Complexity hotspots found: [count]
>
> ## Findings
>
> ### 1. Deep nesting in function
> **File:** `path/to/file.ext`
> **Function:** `FuncName(...)`
> **Complexity:** [brief description — e.g., 4 levels of nesting, 3 nested conditionals]
> **Suggested simplification:** [early returns / extract helper / collapse conditionals]
>
> ### 2. Style outlier
> **File:** `path/to/file.ext`
> **Function:** `FuncName(...)`
> **Why outlier:** [brief explanation]
> **Suggested simplification:** [use existing helper / match codebase convention]
>
> ## Suggested Actions
> - [ ] [Concrete action for each finding]
>
> ## Analysis Metadata
> - Serena tools used: `activate_project`, `get_symbols_overview`, `find_symbol`, `search_for_pattern`
> - Analysis date: [timestamp]

**Noop is the expected outcome most days.** Only create an issue when findings are:
- **Concrete**: You can name the exact functions, files, and what should change.
- **High-impact**: The simplification would meaningfully improve readability, not just satisfy an abstract ideal.
- **Non-controversial**: A maintainer would agree this is a clear improvement without debate.

If findings are marginal or subjective, call `noop`.

${{ inputs.additional-instructions }}
