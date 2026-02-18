---
description: "Analyze Go code for semantic function clustering and refactoring opportunities"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-report.md
engine:
  id: copilot
  model: gpt-5.2-codex
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
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
concurrency:
  group: semantic-function-clustering
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
  serena: ["go"]
network:
  allowed:
    - defaults
    - github
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  noop:
  create-issue:
    max: 1
    title-prefix: "[refactor] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Analyze Go source code to identify semantic function clusters, misplaced functions, and duplicate implementations that warrant refactoring.

### Data Gathering

1. Find all Go files (excluding tests and generated files):
   ```bash
   find . -name "*.go" ! -name "*_test.go" ! -name "*.pb.go" ! -name "*_gen.go" -type f | sort
   ```
2. If no Go files are found, call `noop` with a brief reason and stop.
3. Call Serena `activate_project` with `${{ github.workspace }}`.
4. If there are more than 200 Go files, focus on the 200 largest by line count:
   ```bash
   find . -name "*.go" ! -name "*_test.go" ! -name "*.pb.go" ! -name "*_gen.go" -type f -print0 \
     | xargs -0 wc -l | sort -nr | head -200 | awk '{print $2}'
   ```
5. For each selected file, use `get_symbols_overview` to capture functions and methods.

### How to Analyze

1. Build an inventory by file and directory of:
   - Package name
   - Function and method names (with receivers)
2. Cluster functions by naming patterns and purpose (e.g., `parse*`, `validate*`, `create*`).
3. Identify outliers: functions that do not align with their file's primary purpose.
4. Use Serena (`find_symbol`, `search_for_pattern`, `find_referencing_symbols`) to find duplicates or near-duplicates across files.
5. Focus on high-impact, actionable findings (clear duplication or misplacement).

### What to Skip

- Test or generated files
- Trivial helpers (<5 lines) unless duplicated in multiple places
- Single-occurrence patterns with no clear refactor benefit

### Issue Format

**Issue title:** Semantic function clustering findings (date)

**Issue body:**

> ## Summary
> - Go files analyzed: [count]
> - Functions cataloged: [count]
> - Clusters with issues: [count]
>
> ## Findings
>
> ### 1. Outlier function in wrong file
> **File:** `path/to/file.go`  
> **Function:** `FuncName(...)`  
> **Why outlier:** [brief explanation]  
> **Recommendation:** [move/rename/refactor]  
>
> ### 2. Duplicate or near-duplicate functions
> **Occurrences:** `path/a.go:FuncA`, `path/b.go:FuncB`  
> **Similarity:** [brief summary]  
> **Recommendation:** [consolidate/extract helper]  
>
> ## Suggested Actions
> - [ ] [Concrete action for each finding]
>
> ## Analysis Metadata
> - Serena tools used: `activate_project`, `get_symbols_overview`, `find_symbol`, `search_for_pattern`
> - Analysis date: [timestamp]

Only create an issue when there are clear, actionable findings; otherwise call `noop`.

${{ inputs.additional-instructions }}
