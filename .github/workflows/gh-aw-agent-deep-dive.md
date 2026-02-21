---
name: "Agent Deep Dive"
description: "Deep-dive analysis of a single agent workflow's runs to understand behavior and provide in-depth recommendations"
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
    close-older-issues: true
    expires: 14d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Perform a deep-dive analysis of a single agent workflow to understand how it behaves across all recent runs, then provide in-depth, actionable recommendations.

### Step 0: Select the Target Agent

Use the current week number to pick which agent to analyze this run. This ensures a different agent is analyzed each week.

````bash
# Get the list of available agents by discovering workflow files
AGENTS=$(ls .github/workflows/gh-aw-*.md 2>/dev/null | \
  sed 's|.github/workflows/gh-aw-||; s|\.md$||' | \
  grep -v '^agent-efficiency$' | grep -v '^agent-deep-dive$' | \
  sort)
echo "Available agents:"
echo "$AGENTS"

# Use ISO week number to rotate through the list
WEEK=$(date -u '+%V' | sed 's/^0*//')
COUNT=$(echo "$AGENTS" | wc -l)
INDEX=$(( (WEEK - 1) % COUNT ))
TARGET=$(echo "$AGENTS" | sed -n "$((INDEX + 1))p")
echo "Week $WEEK → index $INDEX → analyzing: $TARGET"
````

Record the selected agent name and use it throughout all subsequent steps.

### Step 1: Gather Run Data

Lookback period: last 14 days. Compute the cutoff date:
````bash
CUTOFF=$(date -u -d '14 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-14d '+%Y-%m-%dT%H:%M:%SZ')
echo "Cutoff: $CUTOFF"
````

Fetch ALL runs (not just failures) for the target workflow file. The workflow file is named `trigger-{TARGET}.yml` or `gh-aw-{TARGET}.lock.yml`:
````bash
# List runs for the trigger workflow
gh api repos/{owner}/{repo}/actions/workflows \
  --jq '.workflows[] | select(.path | test("trigger-TARGET|gh-aw-TARGET")) | {id: .id, name: .name, path: .path}'

# Then fetch runs for each matching workflow
gh api repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs \
  --paginate \
  --jq --arg cutoff "$CUTOFF" '[.workflow_runs[] | select(.created_at >= $cutoff) | {id: .id, name: .name, conclusion: .conclusion, created_at: .created_at, updated_at: .updated_at, html_url: .html_url, run_attempt: .run_attempt}]'
````

Collect all runs: successes, failures, skips, cancellations.

### Step 2: Download Logs for All Non-Skipped Runs

For every run with conclusion other than `skipped` and `action_required`, download and analyze its logs:
````bash
gh api repos/{owner}/{repo}/actions/runs/{run_id}/logs \
  -H "Accept: application/vnd.github+json" \
  > /tmp/gh-aw/agent/logs-{run_id}.zip
unzip -o /tmp/gh-aw/agent/logs-{run_id}.zip -d /tmp/gh-aw/agent/logs-{run_id}/
````

For each run's logs:
- Find the agent/copilot step log
- Count total tool calls made
- List every distinct tool used and how many times
- Note any errors, retries, or unexpected terminations
- Note the final outcome: did the agent produce a meaningful output?
- Record wall-clock duration of the agent step

### Step 3: Deep Analysis

Analyze the collected data to build a complete picture of how this agent behaves. Answer these questions with data:

**Volume and frequency:**
- How many runs occurred in the window? How many succeeded vs. failed?
- What is the typical number of tool calls per run? What is the maximum?
- Are there runs with 2× or 3× the median tool calls? What caused those?

**Tool call patterns:**
- Which tools does this agent call most often?
- Are there repeated identical calls within a single run (same tool, same arguments)?
- Are there calls to tools that always fail or never return useful results?
- Is pagination used correctly, or does the agent hit token limits and stop?

**Error patterns:**
- What errors appear in failed runs? Quote exact messages.
- Do the same errors appear in multiple runs? How many?
- Are errors transient (network, rate limit) or systematic (wrong tool usage, prompt gaps)?

**Output quality (for successful runs):**
- Does the agent's output address the task? (Spot-check 2-3 successful run logs)
- Does the output contain hallucinated or generic content?
- Is the output appropriately sized, or routinely truncated or padded?

**Timing and efficiency:**
- What is the typical wall-clock duration?
- Are there outlier runs that took significantly longer? Why?

### Step 4: Report

File an issue with `create_issue`. The report must be specific, data-backed, and actionable.

**Issue title:** Agent deep dive — {TARGET} — {YYYY-MM-DD}

**Issue body:**

> ## Agent Deep Dive: {TARGET}
>
> **Period:** {cutoff date} to {today}
> **Runs analyzed:** {total count} ({success} success, {failure} failure, {other} other)
> **Median tool calls per run:** {number}
> **Typical duration:** {duration}
>
> ### Run Summary
>
> | Run | Date | Conclusion | Tool Calls | Duration |
> |-----|------|------------|------------|----------|
> | [link](url) | YYYY-MM-DD | success/failure | N | Nm |
> | ... | ... | ... | ... | ... |
>
> ### Tool Call Analysis
>
> | Tool | Total calls | Calls/run (avg) | Errors |
> |------|------------|-----------------|--------|
> | tool_name | N | N | N |
> | ... | ... | ... | ... |
>
> **Repeated identical calls:** [list any tool+args combinations called 2+ times in a single run]
>
> ### Error Analysis
>
> [List each distinct error message, how many runs it appeared in, and whether it is transient or systematic]
>
> ### Output Quality (sample)
>
> [Spot-check 2-3 runs: was the output meaningful, appropriately sized, accurate?]
>
> ### Outlier Runs
>
> [List any runs with unusually high tool calls or duration, with links and brief explanation]
>
> ### Recommendations
>
> [Specific, actionable recommendations based on the data above. Each recommendation must reference specific evidence from the runs analyzed.]
>
> - [ ] [Recommendation with evidence reference]
> - [ ] [Recommendation with evidence reference]

${{ inputs.additional-instructions }}
