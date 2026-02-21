---
name: "Agent Efficiency"
description: "Analyze agent workflow logs for inefficiencies, errors, and prompt improvement opportunities"
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
  group: agent-efficiency
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

Analyze recent agent workflow run logs for excessive tool calls, errors, failures, and bad agent behavior. Focus on understanding what is happening and when — not on recommending fixes.

### Data Gathering

Lookback period: last 3 days. Compute the exact cutoff date using bash before any queries:
````bash
CUTOFF=$(date -u -d '3 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-3d '+%Y-%m-%dT%H:%M:%SZ')
echo "Lookback cutoff: $CUTOFF"
````
Always include the computed date range (`$CUTOFF` to now) in the report so readers know exactly which period the data covers.

1. **List recent agentic workflow runs**

   Use `bash` + `gh api` with `--jq` to list runs efficiently. Filter server-side to avoid large payloads:
   ````bash
   gh api repos/{owner}/{repo}/actions/runs \
     --paginate \
     --jq --arg cutoff "$CUTOFF" '[.workflow_runs[] | select(.created_at >= $cutoff) | select(.path | test("trigger-|gh-aw-")) | {id: .id, name: .name, conclusion: .conclusion, created_at: .created_at, html_url: .html_url, path: .path}]'
   ````

   This captures all agentic workflow runs (trigger files and internal gh-aw workflows). Exclude non-agentic workflows (ci, release, agentics-maintenance) by the path filter.

2. **Understand run conclusions before fetching logs**

   Not all non-success conclusions indicate agent problems:
   - `success` — agent ran to completion
   - `failure` — fetch logs and analyze
   - `cancelled` — usually user-initiated, skip
   - `action_required` — the run was blocked by an approval gate (e.g., first-time contributor). This is NOT an agent failure; skip it
   - `skipped` — pre-conditions not met (e.g., no PR associated). Skip

   Only fetch logs for runs with `failure` conclusion.

3. **Download and analyze job logs**

   Use `gh api` to download logs efficiently:
   ````bash
   gh api repos/{owner}/{repo}/actions/runs/{run_id}/logs \
     -H "Accept: application/vnd.github+json" \
     > /tmp/gh-aw/agent/logs-{run_id}.zip
   unzip -o /tmp/gh-aw/agent/logs-{run_id}.zip -d /tmp/gh-aw/agent/logs-{run_id}/
   ````

   Read the log files to find the agent job's output. Look for the copilot/agent step logs specifically — these contain the tool calls, responses, and agent reasoning.

4. **Check downstream repositories (metadata only)**

   Search for elastic-owned repositories using these workflows:
   ````bash
   gh api search/code -X GET -f q="org:elastic elastic/ai-github-actions language:yaml" --jq '.items[].repository.full_name' | sort -u
   ````

   For each discovered downstream repository, list their agentic workflow runs using the same `gh api` approach from step 1. Collect run metadata (counts, conclusions, pass/fail rates) to include in the report. **Do NOT download or analyze logs from downstream repositories** — your token may not have access, and the logs are too large to process cross-repo. Only fetch and analyze logs for THIS repository.

5. **Use `gh api` with `--jq`, not MCP `actions_list`, for bulk queries**

   The MCP `actions_list` and `actions_get` tools return full JSON objects that frequently exceed the 25,000 token MCP response limit, causing payloads to be dumped to disk. For listing and filtering runs, always prefer `gh api` with `--jq` to extract only the fields you need. Reserve MCP tools for targeted single-item lookups where the response will be small.

### Analysis

Your goal is to accurately describe what is happening across agent runs — not to prescribe fixes. Focus on observable behavior.

For each failed run's logs, read the agent's tool calls, responses, errors, and reasoning. Document:
- **What happened** — Be specific: exact error messages, exact timestamps, exact run URLs. State whether this is a recent failure (today/yesterday) or older.
- **How often** — Is this a one-off or recurring? Count occurrences across the lookback window.
- **Which workflows are affected** — List the workflow names and run URLs.

Look for these specific behavior patterns:
- **Excessive tool calls** — agent making far more calls than necessary to complete a task (e.g., 50+ tool calls for a simple review)
- **Repeated identical tool calls** — agent calling the same tool with the same arguments multiple times in one run
- **Tool call errors** — MCP tool failures, timeouts, API errors; note exact error messages
- **Early failures** — runs failing before the agent step executes (infra/checkout/setup failures)
- **Bad output quality** — truncated responses, hallucinated content, generic non-contextual output
- **Runaway loops** — agent stuck in a loop, exhausting context or turn limits

Look across runs for **recurring patterns**. A single odd failure is noise. The same mistake in 3+ runs across different triggers is a signal.

Skip cancelled runs, infrastructure failures (runner issues, network outages), and `action_required` runs (approval gates, not agent problems).

### Reporting

File an issue with `create_issue`. Always include the exact date range covered at the top of the report.

Include a **per-repository summary** of the metadata you collected — run counts, conclusions, pass/fail rates — for both this repository and any downstream repositories discovered in step 4. This gives visibility into how the workflows are performing across the org.

Each finding must include:
- **What happened** — with exact error messages, log excerpts, and run links
- **When** — timestamps or date range, not just "recently"
- **How often** — count of occurrences in the lookback window
- **Affected workflows** — list of workflow names and run URLs

Do NOT include suggested fixes or impact assessments — this report is for situational awareness only.

Prioritize by frequency: the most recurring problems come first.

If no significant issues are found, still file the issue with the per-repository summary so we have a record. If there are also no downstream repositories using these workflows, call `noop` instead.

${{ inputs.additional-instructions }}
