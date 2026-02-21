---
inlined-imports: true
name: "Agent Deep Dive"
description: "Deep dive a specific agent workflow's recent runs to understand behavior and surface detailed recommendations"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-audit.md
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
      target-workflow:
        description: "Workflow file name to deep dive (e.g. trigger-pr-review.yml). If empty, one is chosen automatically."
        type: string
        required: false
        default: ""
      run-count:
        description: "Number of recent runs to analyze (default: 20)"
        type: string
        required: false
        default: "20"
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
  group: agent-deep-dive
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, actions]
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
    title-prefix: "[agent-deep-dive] "
    close-older-issues: false
    expires: 14d
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
  - name: Select and download workflow logs
    env:
      GH_TOKEN: ${{ github.token }}
      TARGET_WORKFLOW: ${{ inputs.target-workflow }}
      RUN_COUNT: ${{ inputs.run-count }}
    run: |
      set -euo pipefail
      mkdir -p /tmp/gh-aw/deep-dive

      # If no target workflow is specified, pick one automatically by rotating
      # through agentic workflows based on the current day-of-week
      if [ -z "$TARGET_WORKFLOW" ]; then
        mapfile -t WORKFLOWS < <(
          gh api "repos/$GITHUB_REPOSITORY/actions/workflows" \
            --jq '[.workflows[] | select(.path | test("trigger-|gh-aw-")) | .path | ltrimstr(".github/workflows/")] | sort[]'
        )
        COUNT=${#WORKFLOWS[@]}
        if [ "$COUNT" -eq 0 ]; then
          echo "No agentic workflows found." >&2
          exit 0
        fi
        DAY=$(date +%u)   # 1=Mon … 7=Sun
        IDX=$(( (DAY - 1) % COUNT ))
        TARGET_WORKFLOW="${WORKFLOWS[$IDX]}"
      fi

      echo "TARGET_WORKFLOW=$TARGET_WORKFLOW" >> "$GITHUB_ENV"
      echo "Analyzing workflow: $TARGET_WORKFLOW" >&2

      # Fetch the last N runs for this workflow (all conclusions)
      gh api "repos/$GITHUB_REPOSITORY/actions/workflows/$TARGET_WORKFLOW/runs" \
        --jq "[.workflow_runs[:$RUN_COUNT] | .[] | {id:.id, name:.name, conclusion:.conclusion, created_at:.created_at, html_url:.html_url}]" \
        > /tmp/gh-aw/deep-dive/runs.json

      echo "Runs fetched: $(jq length /tmp/gh-aw/deep-dive/runs.json)" >&2

      # Download logs for failed runs only (up to 10)
      jq -r '[.[] | select(.conclusion == "failure")] | .[:10] | .[].id' \
        /tmp/gh-aw/deep-dive/runs.json | while read -r run_id; do
        mkdir -p "/tmp/gh-aw/deep-dive/logs/$run_id"
        gh api "repos/$GITHUB_REPOSITORY/actions/runs/$run_id/logs" \
          -H "Accept: application/vnd.github+json" \
          > "/tmp/gh-aw/deep-dive/logs/$run_id/logs.zip" 2>/dev/null || continue
        unzip -q -o "/tmp/gh-aw/deep-dive/logs/$run_id/logs.zip" \
          -d "/tmp/gh-aw/deep-dive/logs/$run_id/" 2>/dev/null || true
        rm -f "/tmp/gh-aw/deep-dive/logs/$run_id/logs.zip"
      done

      # Build manifest for error extractor
      jq '[.[] | select(.conclusion == "failure")] | .[:10] | map({run_id:.id, conclusion:.conclusion, created_at:.created_at, html_url:.html_url, log_files:[]})' \
        /tmp/gh-aw/deep-dive/runs.json > /tmp/gh-aw/deep-dive/manifest.json

      # Populate log_files paths
      python3 - <<'EOF'
      import json, pathlib
      with open("/tmp/gh-aw/deep-dive/manifest.json") as f:
          manifest = json.load(f)
      for entry in manifest:
          run_dir = pathlib.Path(f"/tmp/gh-aw/deep-dive/logs/{entry['run_id']}")
          entry["log_files"] = [str(p) for p in sorted(run_dir.rglob("*.txt"))]
      with open("/tmp/gh-aw/deep-dive/manifest.json", "w") as f:
          json.dump(manifest, f, indent=2)
      EOF

      # Extract errors with context
      python3 scripts/extract-log-errors.py \
        --manifest /tmp/gh-aw/deep-dive/manifest.json \
        --context 10 \
        --output /tmp/gh-aw/deep-dive/errors.json \
        || true

      echo "Errors extracted: $(jq '.total_matches // 0' /tmp/gh-aw/deep-dive/errors.json 2>/dev/null || echo 0)" >&2
---

Perform a deep dive on a single agent workflow to understand how it is behaving across recent runs and surface specific, actionable recommendations.

### Context

- **Target workflow:** `${{ env.TARGET_WORKFLOW }}`
- **Runs analyzed:** up to `${{ inputs.run-count }}` most recent runs
- **Pre-downloaded data:**
  - `/tmp/gh-aw/deep-dive/runs.json` — run list with conclusions and links
  - `/tmp/gh-aw/deep-dive/errors.json` — error snippets from failed runs with surrounding context
  - `/tmp/gh-aw/deep-dive/logs/<run_id>/` — raw log files for each failed run

### Data Gathering

1. **Read the pre-loaded data**

   Start with:
   - `/tmp/gh-aw/deep-dive/runs.json` for the full run list and conclusions
   - `/tmp/gh-aw/deep-dive/errors.json` for structured error snippets
   - `/tmp/gh-aw/deep-dive/logs/<run_id>/` for raw agent step logs

2. **Read the workflow definition**

   Read the workflow's source `.md` file from `.github/workflows/` (e.g., if target is `trigger-pr-review.yml`, read `gh-aw-pr-review.md`). This gives you the prompt text, fragments imported, safe outputs configured, and tool permissions — necessary context for understanding why the agent behaved as it did.

3. **Trace agent tool calls in successful runs**

   For a sample of successful runs (up to 3), read the agent step logs to understand the normal tool call sequence: how many turns, which tools are used, how the agent reaches its output. This establishes a baseline.

4. **Trace tool calls in failed runs**

   For each failed run, trace the sequence of tool calls and agent responses from the agent step logs. Note:
   - Total number of tool calls
   - Repeated/redundant calls (same tool, same arguments)
   - Calls that produced errors or empty results
   - Where in the sequence the failure occurred

5. **Read the workflow's README for stated purpose and trigger**

   Find the workflow's directory under `gh-agent-workflows/` and read `README.md` to understand the intended scope and outputs. Compare against what you see in the logs.

### Analysis

Produce a thorough behavioral analysis of the target workflow. For each dimension below, describe what you actually observed in the logs:

- **Run outcomes** — summary table of recent runs (date, conclusion, run link)
- **Failure modes** — for each failed run: what step failed, exact error message, log excerpt
- **Tool call patterns** — average and outlier turn counts; which tools are called most; any tools called redundantly
- **Prompt adherence** — does the agent follow the workflow's instructions? Where does it deviate?
- **Output quality** — for successful runs: does the output match the expected safe-output format? Are issues/comments/PRs well-formed?
- **Recurring patterns** — note any pattern appearing in 2+ runs

### Reporting

File an issue with `create_issue`. The issue title must follow the format:
`Agent deep dive: <workflow-name> - YYYY-MM-DD`

**Issue body format:**

> ## Agent Deep Dive: `<workflow-name>`
> **Date:** YYYY-MM-DD
> **Runs analyzed:** N total (X success, Y failure, Z other)
>
> ## Run Outcomes
> | Run | Date | Conclusion |
> |-----|------|------------|
> | [link](url) | date | conclusion |
>
> ## Failure Analysis
> For each failed run: step name, error excerpt, likely cause.
>
> ## Tool Call Patterns
> - Average turns per run: N
> - Most-called tools: tool1 (N times), tool2 (N times)
> - Anomalies: [any outliers or redundant calls]
>
> ## Behavioral Observations
> What the agent does well and where it struggles, with log evidence.
>
> ## Recurring Patterns
> Patterns seen in 2+ runs.

Do not include suggested fixes or action items — focus on accurate description of observed behavior.

If the workflow has no recent runs at all, call `noop` with the reason.

${{ inputs.additional-instructions }}
