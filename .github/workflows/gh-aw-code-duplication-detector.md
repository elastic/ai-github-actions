---
inlined-imports: true
name: "Code Duplication Detector"
description: "Analyze source code for duplication patterns and refactoring opportunities"
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
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      title-prefix:
        description: "Title prefix for created issues (e.g. '[refactor]')"
        type: string
        required: false
        default: "[refactor]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: code-duplication-detector
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
  serena: ["go", "python", "typescript", "java", "csharp", "rust"]
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

Analyze source code to identify semantic function clusters, misplaced functions, and duplicate implementations that warrant refactoring.

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
7. Use the **Pick Three, Keep Many** pattern for the analysis phase: spawn 3 `general-purpose` sub-agents, each searching for duplication from a different angle (e.g., one scanning different directories or modules for cross-boundary duplication, one using exact/near-exact match heuristics on function bodies, one looking for structural or semantic similarity across naming clusters). Include the file list, symbol inventory, and the full "How to Analyze" / "What to Skip" criteria in each sub-agent prompt. Each sub-agent should return all findings that meet the quality criteria.

### How to Analyze

1. Build an inventory by file and directory of:
   - Module/package/namespace (when applicable)
   - Function and method names (with receivers/classes if relevant)
2. Cluster functions by naming patterns and purpose (e.g., `parse*`, `validate*`, `create*`).
3. Identify outliers: functions that do not align with their file's primary purpose.
4. Use Serena (`find_symbol`, `search_for_pattern`, `find_referencing_symbols`) when supported to find duplicates or near-duplicates across files.
5. Focus on high-impact, actionable findings (clear duplication or misplacement).

### What to Skip

- Test or generated files
- Trivial helpers (<5 lines) unless duplicated in multiple places
- Single-occurrence patterns with no clear refactor benefit
- Subjective code organization preferences — only flag placements that are clearly wrong, not "could be slightly better"
- Near-duplicates that exist for good reasons (different error handling, different types, intentional specialization)

### Issue Format

**Issue title:** Code duplication findings (date)

**Issue body:**

> ## Summary
> - Files analyzed: [count]
> - Functions cataloged: [count]
> - Clusters with issues: [count]
>
> ## Findings
>
> ### 1. Outlier function in wrong file
> **File:** `path/to/file.ext`  
> **Function:** `FuncName(...)`  
> **Why outlier:** [brief explanation]  
> **Recommendation:** [move/rename/refactor]  
>
> ### 2. Duplicate or near-duplicate functions
> **Occurrences:** `path/a.ext:FuncA`, `path/b.ext:FuncB`  
> **Similarity:** [brief summary]  
> **Recommendation:** [consolidate/extract helper]  
>
> ## Suggested Actions
> - [ ] [Concrete action for each finding]
>
> ## Analysis Metadata
> - Serena tools used: `activate_project`, `get_symbols_overview`, `find_symbol`, `search_for_pattern`
> - Analysis date: [timestamp]

**Noop is the expected outcome most days.** Only create an issue when findings are:
- **Concrete**: You can name the exact functions, files, and what should change.
- **High-impact**: The refactor would meaningfully improve maintainability, not just satisfy an abstract ideal.
- **Non-controversial**: A maintainer would agree this is a clear improvement without debate.

If findings are marginal or subjective, call `noop`.

${{ inputs.additional-instructions }}
