---
inlined-imports: true
name: "Internal: Agent Efficiency"
description: "Analyze agent workflow logs for inefficiencies, errors, and prompt improvement opportunities"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/scheduled-audit.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  schedule:
    - cron: "daily around 16:00 on weekdays"
  workflow_dispatch:
  roles: [admin, maintainer, write]
  bots:
    - "github-actions[bot]"
concurrency:
  group: ${{ github.workflow }}-agent-efficiency
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
    title-prefix: "[agent-efficiency] "
    close-older-issues: false
    expires: 7d
timeout-minutes: 60
steps:
  - name: Download failed run logs
    env:
      GH_TOKEN: ${{ github.token }}
    run: |
      set -euo pipefail
      SINCE=$(date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || true)
      if [ -z "$SINCE" ]; then
        echo "Error: Failed to calculate lookback date" >&2
        exit 1
      fi
      echo "SINCE=$SINCE" >> "$GITHUB_ENV"

      mkdir -p /tmp/gh-aw/logs

      # List all failed agentic workflow runs in the lookback window (up to 20)
      gh api "repos/$GITHUB_REPOSITORY/actions/runs" \
        --paginate \
        --jq "[.workflow_runs[] | select(.created_at >= \"$SINCE\") | select(.path | test(\"trigger-|gh-aw-\")) | select(.conclusion == \"failure\") | {id:.id, name:.name, conclusion:.conclusion, created_at:.created_at, html_url:.html_url, path:.path}]" \
        | jq -s 'add // [] | .[:20]' > /tmp/gh-aw/failed_runs.json

      echo "Failed runs found: $(jq length /tmp/gh-aw/failed_runs.json)"

      # Download logs for each failed run
      jq -r '.[].id' /tmp/gh-aw/failed_runs.json | while read -r run_id; do
        mkdir -p "/tmp/gh-aw/logs/$run_id"
        gh api "repos/$GITHUB_REPOSITORY/actions/runs/$run_id/logs" \
          -H "Accept: application/vnd.github+json" \
          > "/tmp/gh-aw/logs/$run_id/logs.zip" 2>/dev/null || continue
        unzip -q -o "/tmp/gh-aw/logs/$run_id/logs.zip" \
          -d "/tmp/gh-aw/logs/$run_id/" 2>/dev/null || true
        rm -f "/tmp/gh-aw/logs/$run_id/logs.zip"
      done

      # Build a manifest for the error extractor
      jq '[.[] | {run_id:.id, conclusion:.conclusion, created_at:.created_at, html_url:.html_url, log_files:[]}]' \
        /tmp/gh-aw/failed_runs.json > /tmp/gh-aw/logs/manifest.json

      # Populate log_files in manifest from downloaded files
      python3 - <<'EOF'
      import json, os, pathlib
      with open("/tmp/gh-aw/logs/manifest.json") as f:
          manifest = json.load(f)
      for entry in manifest:
          run_dir = pathlib.Path(f"/tmp/gh-aw/logs/{entry['run_id']}")
          entry["log_files"] = [str(p) for p in sorted(run_dir.rglob("*.txt"))]
      with open("/tmp/gh-aw/logs/manifest.json", "w") as f:
          json.dump(manifest, f, indent=2)
      EOF

      # Extract error lines with surrounding context
      python3 scripts/extract-log-errors.py \
        --manifest /tmp/gh-aw/logs/manifest.json \
        --context 8 \
        --output /tmp/gh-aw/errors.json \
        || true

      echo "Errors extracted: $(jq '.total_matches // 0' /tmp/gh-aw/errors.json 2>/dev/null || echo 0)"
---

Analyze recent agent workflow run logs for bad agent behavior, excessive tool calls, recurring errors, and patterns that indicate prompt or tooling improvements are needed.

### Context

- **Lookback window:** runs since `${{ env.SINCE }}` (last 7 days)
- **Pre-downloaded logs:** `/tmp/gh-aw/logs/` contains logs for up to 20 recently failed runs
- **Pre-extracted errors:** `/tmp/gh-aw/errors.json` contains error snippets with surrounding context
- **Run metadata:** `/tmp/gh-aw/failed_runs.json` contains all failed run metadata for the lookback window

### Data Gathering

1. **Read the pre-extracted error data**

   Start by reading `/tmp/gh-aw/errors.json`. This file was produced by the setup step and contains error snippets from all downloaded failed runs, each with surrounding context lines. Use this as your primary source for failure analysis.

   Also read `/tmp/gh-aw/failed_runs.json` for the list of failed runs and their metadata.

2. **Read agent step logs for behavioral analysis**

   For each failed run, find the agent/copilot step log files in `/tmp/gh-aw/logs/<run_id>/`. Look for files containing "copilot" or "agent" in their name. These logs contain:
   - Tool calls made by the agent (list_issues, search_code, bash, etc.)
   - The agent's reasoning and responses
   - How many turns were used before the run ended

3. **Collect run summary statistics**

   From the metadata in `/tmp/gh-aw/failed_runs.json` and from listing runs with `gh api`:
   ````bash
   SINCE="${{ env.SINCE }}"
   gh api "repos/$GITHUB_REPOSITORY/actions/runs" \
     --paginate \
     --jq "[.workflow_runs[] | select(.created_at >= \"$SINCE\") | select(.path | test(\"trigger-|gh-aw-\")) | {conclusion:.conclusion, path:.path}]" \
     | jq -s 'add // [] | group_by(.path) | map({path: .[0].path, conclusions: (group_by(.conclusion) | map({conclusion: .[0].conclusion, count: length}))})' \
   ````

4. **Check downstream repositories (metadata only)**

   Search for elastic-owned repositories using these workflows:
   ````bash
   gh api search/code -X GET -f q="org:elastic elastic/ai-github-actions language:yaml" --jq '.items[].repository.full_name' | sort -u
   ````

   For each discovered downstream repository, list their agentic workflow runs using the same `gh api` approach. Collect run metadata (counts, conclusions, pass/fail rates) only. **Do NOT download or analyze logs from downstream repositories.**

5. **Use `gh api` with `--jq`, not MCP `actions_list`, for bulk queries**

   The MCP `actions_list` and `actions_get` tools return full JSON objects that frequently exceed the 25,000 token MCP response limit. For listing and filtering runs, always prefer `gh api` with `--jq`. Reserve MCP tools for targeted single-item lookups.

### Analysis

Your goal is to identify patterns of **bad agent behavior** across all failed runs. Focus on:

- **Excessive tool calls** — agent spending far more turns than needed (e.g., re-reading the same file repeatedly, running the same search multiple times). Count tool calls per run and flag outliers.
- **Wrong tool usage** — agent using MCP tools for bulk data that cause token limit dumps, instead of `gh api` + `bash`; or fetching data it doesn't use
- **Failure to follow instructions** — agent ignoring explicit constraints in the prompt (e.g., not calling noop when it should, not including required fields)
- **Errors and crashes** — infrastructure errors, API rate limits, checkout failures, command not found, exit code failures
- **Bad output quality** — agent producing reports that are vague, unactionable, hallucinated, or formatted incorrectly

For each pattern, identify how many runs exhibit it, which workflows are affected, and what the root cause is (prompt gap, missing example, confusing instruction).

**Skip:** successful runs, cancelled runs, `action_required` runs (approval gates), `skipped` runs, and one-off infrastructure failures with no pattern.

### Reporting

File an issue with `create_issue`.

Include a **per-repository run summary** table showing counts and pass/fail rates for this repo and any discovered downstream repos, covering the lookback window `${{ env.SINCE }}` to now. Make clear these are runs from the last 7 days, not a longer historical window.

For each behavioral pattern found, include:
- What happened (with exact log excerpt and run link)
- How many runs/workflows are affected
- Root cause (specific file/fragment/instruction that caused it)

Do not include suggested fixes or impact assessments — focus on accurate description of observed behavior.

If no significant patterns are found, still file the issue with the run summary table. If there are also no downstream repositories, call `noop` instead.
