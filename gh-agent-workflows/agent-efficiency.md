---
description: "Analyze agent workflow logs for inefficiencies, errors, and prompt improvement opportunities"
imports:
  - gh-aw-workflows/scheduled-report-rwx.md
engine:
  id: copilot
  model: gpt-5.2-codex
on:
  schedule:
    - cron: "0 16 * * 1-5"
  workflow_dispatch:
concurrency:
  group: agent-efficiency
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
strict: false
roles: [admin, maintainer, write]
safe-outputs:
  create-issue:
    max: 1
    title-prefix: "[agent-efficiency] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

Analyze recent agent workflow run logs for inefficiencies, recurring errors, and patterns that indicate prompt improvements are needed.

### Data Gathering

Lookback 3 days.

1. **List recent agentic workflow runs**

   Use `bash` to call the GitHub API and list recent workflow runs for each agentic workflow in this repository:
   ```bash
   gh api repos/{owner}/{repo}/actions/runs \
     --jq '.workflow_runs[] | select(.created_at >= "DATE") | {id: .id, name: .name, conclusion: .conclusion, created_at: .created_at, html_url: .html_url}'
   ```

   Filter to agentic workflow runs only (pr-review, issue-triage, mention-in-pr, mention-in-issue, docs-drift, downstream-health, stale-issues, agent-efficiency). Exclude non-agentic workflows (ci, release, agentics-maintenance).

2. **Download and analyze job logs**

   For each workflow run, download the logs:
   ```bash
   gh api repos/{owner}/{repo}/actions/runs/{run_id}/logs -H "Accept: application/vnd.github+json" > /tmp/logs-{run_id}.zip
   unzip -o /tmp/logs-{run_id}.zip -d /tmp/logs-{run_id}/
   ```

   Read the log files to find the agent job's output. Look for the copilot/agent step logs specifically — these contain the tool calls, responses, and agent reasoning.

3. **Also check for downstream repositories**

   Search for elastic-owned repositories using these workflows:
   ```
   github-search_code: query="org:elastic elastic/ai-github-actions language:yaml"
   ```

   For each discovered downstream repository, repeat steps 1-2 to gather their agentic workflow logs as well.

### What to Look For

Analyze each agent run's logs for these categories of problems:

#### 1. Hallucinated or Imaginary Tool Calls
- Calling tools that don't exist (tool names not in the workflow's tool list)
- Using wrong method names or parameters on real tools
- Inventing API endpoints or MCP tool methods
- **Pattern**: Look for tool call errors like "tool not found", "unknown method", or "invalid parameter"

#### 2. Safe-Output Misunderstanding
- Attempting actions the workflow doesn't have permission for (e.g., trying to push in a read-only workflow)
- Calling safe-output tools with invalid parameters
- Exceeding safe-output limits (max comments, max review submissions)
- Trying to modify `.github/workflows/` files and getting rejected
- **Pattern**: Look for safe-output validation errors, permission denials, or "max exceeded" messages

#### 3. Excessive Retries and Wasted Turns
- Repeating the same failed tool call multiple times without changing approach
- Pagination failures — hitting the 25,000 token limit and retrying without reducing `per_page`
- Making the same API call with identical parameters expecting different results
- **Pattern**: Look for identical consecutive tool calls, or the same error appearing 3+ times

#### 4. Context Window Waste
- Reading entire large files when only a small section was needed
- Fetching all pages of results when only the first page was needed
- Requesting data that was already available from a previous call
- **Pattern**: Look for very large tool responses followed by the agent using only a small portion

#### 5. Misunderstanding Workflow Role
- A review agent trying to push code
- A triage agent trying to create PRs
- An agent generating output in a format the safe-outputs don't support
- **Pattern**: Look for the agent attempting actions outside its declared CAN/CANNOT constraints

#### 6. Error Recovery Failures
- Agent hitting an error and giving up without trying alternatives
- Agent producing empty or placeholder output after encountering an error
- Agent apologizing for limitations instead of working within them
- **Pattern**: Look for error messages followed by no further tool calls, or responses that mention being "unable to" do something the workflow supports

### What to Skip

- Successful runs with no errors or inefficiencies
- Runs that were cancelled (user-initiated, not agent failure)
- Infrastructure failures unrelated to the agent (runner issues, network outages, GitHub API downtime)
- Minor inefficiencies that don't meaningfully impact cost or quality (e.g., one extra API call)
- Known limitations that are already documented (e.g., fork PR push restriction)

### Issue Format

**Issue title:** Agent efficiency report — [date range]

**Issue body:**

> ## Agent Efficiency Report
>
> Analysis of agentic workflow run logs for [date range]. This report identifies recurring errors, inefficiencies, and patterns that could be addressed through prompt improvements.
>
> ### Runs Analyzed
>
> | Repository | Workflow | Runs | Failures | Issues Found |
> | --- | --- | --- | --- | --- |
> | [repo] | [workflow] | [count] | [count] | [count] |
>
> ### Findings
>
> #### 1. [Category] — [Brief description]
>
> **Frequency:** [How often this occurred across runs]
> **Workflow(s):** [Which workflow(s) are affected]
> **Example:** [Link to a specific run showing the problem]
> **Log excerpt:**
> ```
> [Relevant log lines showing the issue]
> ```
> **Root cause:** [Why the agent is doing this — what in the prompt or tooling causes it]
> **Suggested fix:** [Specific prompt change, fragment update, or tooling adjustment]
>
> #### 2. [Next finding...]
>
> ### Summary
>
> - Total runs analyzed: [count]
> - Runs with issues: [count]
> - Most common problem category: [category]
> - Estimated wasted tokens/turns: [rough estimate if possible]
>
> ### Suggested Actions
>
> - [ ] [Specific, actionable improvement with file reference]
> - [ ] [Next action...]

**Guidelines:**
- Focus on **recurring patterns**, not one-off errors
- Always include a specific log excerpt demonstrating the problem
- Suggest concrete prompt or fragment changes — reference specific files (e.g., "Update `gh-aw-fragments/review-process.md` to clarify X")
- Group related findings (e.g., all pagination issues together)
- Prioritize by frequency and impact — most common problems first
- If no significant issues found, call `noop` with message "Agent efficiency check complete — no significant issues found in recent runs"
