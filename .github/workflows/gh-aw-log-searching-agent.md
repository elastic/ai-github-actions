---
inlined-imports: true
name: "Log Searching Agent"
description: "Search workflow logs for specific terms and investigate matches"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
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
      workflow:
        description: "Workflow file name to search logs for (e.g. ci.yml)"
        type: string
        required: true
      search-terms:
        description: "Comma-separated list of exact match search terms to look for in logs"
        type: string
        required: true
      days:
        description: "Number of days to look back for workflow runs"
        type: number
        required: false
        default: 7
      max-runs:
        description: "Maximum number of workflow runs to download logs from"
        type: number
        required: false
        default: 20
      conclusion:
        description: "Filter runs by conclusion (failure, success, cancelled, any)"
        type: string
        required: false
        default: "failure"
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
        description: "Title prefix for created issues (e.g. '[log-search]')"
        type: string
        required: false
        default: "[log-search]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-log-searching-agent
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
tools:
  github:
    toolsets: [repos, issues, search, actions]
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
  - name: Search workflow logs
    env:
      GH_TOKEN: ${{ github.token }}
      SEARCH_WORKFLOW: ${{ inputs.workflow }}
      SEARCH_TERMS: ${{ inputs.search-terms }}
      SEARCH_DAYS: ${{ inputs.days }}
      SEARCH_MAX_RUNS: ${{ inputs.max-runs }}
      SEARCH_CONCLUSION: ${{ inputs.conclusion }}
    run: |
      set -euo pipefail

      LOGS_DIR="/tmp/gh-aw/logs"
      RESULTS_DIR="/tmp/gh-aw/search-results"
      mkdir -p "$LOGS_DIR" "$RESULTS_DIR"

      # Compute the since date (N days ago)
      SINCE_DATE=$(date -u -d "$SEARCH_DAYS days ago" +%Y-%m-%dT00:00:00Z 2>/dev/null \
        || date -u -v-"${SEARCH_DAYS}"d +%Y-%m-%dT00:00:00Z)

      echo "Fetching up to $SEARCH_MAX_RUNS runs of '$SEARCH_WORKFLOW' since $SINCE_DATE (conclusion: $SEARCH_CONCLUSION)..."

      # List matching workflow runs
      PAGE=1
      COLLECTED=0
      RUN_IDS=""
      while [ "$COLLECTED" -lt "$SEARCH_MAX_RUNS" ]; do
        RESPONSE=$(gh api "repos/$GITHUB_REPOSITORY/actions/workflows/$SEARCH_WORKFLOW/runs?per_page=100&page=$PAGE&created=>=$SINCE_DATE" --jq '.workflow_runs')
        COUNT=$(echo "$RESPONSE" | jq 'length')
        [ "$COUNT" -gt 0 ] || break

        for i in $(seq 0 $((COUNT - 1))); do
          RUN_CONCLUSION=$(echo "$RESPONSE" | jq -r ".[$i].conclusion")
          RUN_ID=$(echo "$RESPONSE" | jq -r ".[$i].id")

          if [ "$SEARCH_CONCLUSION" = "any" ] || [ "$RUN_CONCLUSION" = "$SEARCH_CONCLUSION" ]; then
            RUN_IDS="$RUN_IDS $RUN_ID"
            COLLECTED=$((COLLECTED + 1))
            [ "$COLLECTED" -lt "$SEARCH_MAX_RUNS" ] || break
          fi
        done
        PAGE=$((PAGE + 1))
      done

      if [ -z "$RUN_IDS" ]; then
        echo "No matching workflow runs found."
        echo '{"workflow":"'"$SEARCH_WORKFLOW"'","search_terms":[],"since":"'"$SINCE_DATE"'","runs_searched":0,"total_matches":0,"results":[]}' > "$RESULTS_DIR/search-manifest.json"
        exit 0
      fi

      echo "Found $COLLECTED matching run(s). Downloading and searching logs..."

      # Parse search terms (comma-separated) into an array
      IFS=',' read -ra TERMS <<< "$SEARCH_TERMS"
      # Trim whitespace from each term
      CLEAN_TERMS=()
      for term in "${TERMS[@]}"; do
        cleaned=$(echo "$term" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        [ -n "$cleaned" ] && CLEAN_TERMS+=("$cleaned")
      done

      MANIFEST_ENTRIES=""
      TOTAL_MATCHES=0

      for RUN_ID in $RUN_IDS; do
        RUN_DIR="$LOGS_DIR/$RUN_ID"
        mkdir -p "$RUN_DIR"

        # Download and extract logs
        echo "  Downloading logs for run $RUN_ID..."
        if ! gh api "repos/$GITHUB_REPOSITORY/actions/runs/$RUN_ID/logs" > "$RUN_DIR/logs.zip" 2>/dev/null; then
          echo "  Warning: could not download logs for run $RUN_ID"
          continue
        fi

        if ! unzip -q -o "$RUN_DIR/logs.zip" -d "$RUN_DIR/" 2>/dev/null; then
          echo "  Warning: could not extract logs for run $RUN_ID"
          continue
        fi
        rm -f "$RUN_DIR/logs.zip"

        # Search each log file for each term
        RUN_MATCHES=""
        RUN_MATCH_COUNT=0
        while IFS= read -r -d '' logfile; do
          for term in "${CLEAN_TERMS[@]}"; do
            MATCHES=$(grep -n -F "$term" "$logfile" 2>/dev/null || true)
            if [ -n "$MATCHES" ]; then
              MATCH_COUNT=$(echo "$MATCHES" | wc -l)
              RUN_MATCH_COUNT=$((RUN_MATCH_COUNT + MATCH_COUNT))
              RELATIVE_PATH="${logfile#$LOGS_DIR/}"

              # Write matched lines with context to a result file
              RESULT_FILE="$RESULTS_DIR/run-${RUN_ID}-matches.txt"
              {
                echo "=== File: $RELATIVE_PATH | Term: $term | Matches: $MATCH_COUNT ==="
                grep -n -F -B2 -A2 "$term" "$logfile" 2>/dev/null || true
                echo ""
              } >> "$RESULT_FILE"

              # Build JSON entry for this file match
              ESCAPED_PATH=$(echo "$RELATIVE_PATH" | jq -Rs '.')
              ESCAPED_TERM=$(echo "$term" | jq -Rs '.')
              RUN_MATCHES="$RUN_MATCHES{\"file\":$ESCAPED_PATH,\"term\":$ESCAPED_TERM,\"count\":$MATCH_COUNT},"
            fi
          done
        done < <(find "$RUN_DIR" -name "*.txt" -print0)

        if [ "$RUN_MATCH_COUNT" -gt 0 ]; then
          TOTAL_MATCHES=$((TOTAL_MATCHES + RUN_MATCH_COUNT))
          RUN_MATCHES="${RUN_MATCHES%,}"
          RUN_URL="https://github.com/$GITHUB_REPOSITORY/actions/runs/$RUN_ID"
          MANIFEST_ENTRIES="$MANIFEST_ENTRIES{\"run_id\":$RUN_ID,\"url\":\"$RUN_URL\",\"match_count\":$RUN_MATCH_COUNT,\"file_matches\":[$RUN_MATCHES]},"
          echo "  Run $RUN_ID: $RUN_MATCH_COUNT match(es)"
        else
          echo "  Run $RUN_ID: no matches"
          # Clean up log files for runs with no matches to save disk
          rm -rf "$RUN_DIR"
        fi
      done

      # Build search terms JSON array
      TERMS_JSON="["
      for term in "${CLEAN_TERMS[@]}"; do
        ESCAPED=$(echo "$term" | jq -Rs '.')
        TERMS_JSON="$TERMS_JSON$ESCAPED,"
      done
      TERMS_JSON="${TERMS_JSON%,}]"

      # Write the search manifest
      MANIFEST_ENTRIES="${MANIFEST_ENTRIES%,}"
      cat > "$RESULTS_DIR/search-manifest.json" <<MANIFEST_EOF
      {
        "workflow": "$SEARCH_WORKFLOW",
        "search_terms": $TERMS_JSON,
        "since": "$SINCE_DATE",
        "conclusion_filter": "$SEARCH_CONCLUSION",
        "runs_searched": $COLLECTED,
        "total_matches": $TOTAL_MATCHES,
        "results": [$MANIFEST_ENTRIES]
      }
      MANIFEST_EOF

      echo ""
      echo "Search complete. Total matches: $TOTAL_MATCHES across $COLLECTED run(s)."
      echo "Results written to $RESULTS_DIR/"
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

## Report Assignment

Investigate workflow log search results and file an actionable triage issue when patterns or recurring problems are found.

### Context

A preflight search has already been performed on workflow logs for **${{ inputs.workflow }}** in `${{ github.repository }}`. The search looked for the following terms across the last **${{ inputs.days }}** day(s), filtered to runs with conclusion **${{ inputs.conclusion }}**:

**Search terms:** `${{ inputs.search-terms }}`

### Data Gathering

1. Read `/tmp/gh-aw/search-results/search-manifest.json` to understand the search summary:
   - How many runs were searched
   - How many total matches were found
   - Which runs had matches and how many
2. For each run with matches, read the corresponding `/tmp/gh-aw/search-results/run-<run_id>-matches.txt` file to see the actual matching log lines with context.
3. If further investigation is needed, use the `github` Actions APIs to fetch additional run details (timing, triggering commit, branch, etc.).

### What to Look For

- **Recurring patterns**: The same error or warning appearing across multiple runs, suggesting a persistent or systemic issue.
- **Frequency trends**: Whether matches are increasing, decreasing, or stable over time.
- **Root causes**: Correlate matches with specific commits, branches, configuration changes, or environmental factors.
- **Impact assessment**: How the matched log entries relate to build failures, test failures, or degraded performance.
- **Actionable clusters**: Group related matches that point to the same underlying problem.

### Analysis Rules

- Only report findings backed by concrete evidence from the search results — exact log lines, run IDs, and timestamps.
- Do not speculate about causes without supporting log evidence.
- If the search returned zero matches, call `noop` — do not fabricate findings.
- If matches exist but reveal nothing actionable (e.g., benign warnings, already-resolved issues), call `noop` with a brief explanation.

### Quality Gate — When to Noop

Call `noop` when:
- Zero matches were found across all searched runs
- Matches are benign or informational with no action needed
- All matched issues are already tracked by existing open issues
- The evidence is insufficient to identify a root cause or actionable pattern

### Issue Format

**Issue title:** Brief summary of the log search findings for `${{ inputs.workflow }}`

**Issue body:**

> ## Log Search Investigation Report
>
> **Workflow:** ${{ inputs.workflow }}
> **Search terms:** ${{ inputs.search-terms }}
> **Window:** ${{ inputs.days }} day(s), conclusion: ${{ inputs.conclusion }}
> **Runs searched:** [count from manifest]
> **Total matches:** [count from manifest]
>
> ### Findings
>
> #### 1. [Pattern or issue description]
> **Frequency:** [N matches across M runs]
> **Evidence:**
> - Run [link]: [relevant log excerpt]
> - Run [link]: [relevant log excerpt]
>
> **Root cause:** [if identifiable from evidence]
> **Impact:** [what this means for CI/builds/tests]
>
> ### Suggested Actions
> - [ ] [Concrete action item]
> - [ ] [Validation step]

${{ inputs.additional-instructions }}
