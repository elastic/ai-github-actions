---
description: "Monitor downstream repositories using AI workflows and report quality issues"
imports:
  - gh-aw-workflows/scheduled-report-rwx.md
engine:
  id: copilot
  model: gpt-5.3-codex
on:
  schedule:
    - cron: "0 10 * * *"  # Daily at 10:00 UTC
  workflow_dispatch:
concurrency:
  group: downstream-health
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
    title-prefix: "[downstream-health] "
    close-older-issues: true
    expires: 7d
timeout-minutes: 30
---

Monitor the health of downstream repositories using AI workflows from elastic/ai-github-actions and report quality issues.

### Data Gathering

1. **Discover downstream repositories**
   
   Search for elastic-owned repositories using these AI workflows:
   ```
   github-search_code: query="org:elastic elastic/ai-github-actions language:yaml"
   ```
   
   Extract unique repository names (excluding elastic/ai-github-actions itself). Known repos include:
   - elastic/integrations
   - elastic/infra-party

2. **For each downstream repository, check recent bot activity**
   
   Look for recent comments and PR reviews by `github-actions[bot]` in the last 24 hours:
   - Use `github-search_issues` with query: `repo:{owner}/{repo} commenter:github-actions[bot] updated:>={date}`
   - Use `github-search_pull_requests` with query: `repo:{owner}/{repo} reviewed-by:github-actions[bot] updated:>={date}`
   
3. **Analyze bot responses for issues**
   
   For each bot comment or review found:
   - Read the full comment/review text using `github-issue_read` (method: `get_comments`) or `github-pull_request_read` (method: `get_reviews` or `get_review_comments`)
   - Check for any user reactions or follow-up comments indicating problems
   - Look for tool errors, error messages, stack traces, or other signs of failure
   - Check if the response appears low quality, incomplete, or unhelpful

### What to Look For

Flag bot responses that show any of these issues:

1. **Tool Errors**
   - MCP tool failures, timeouts, or error messages
   - Bash command failures or permission errors
   - API rate limit errors
   - Network errors or timeouts

2. **Quality Issues**
   - Incomplete or truncated responses
   - Responses that don't address the user's question
   - Hallucinated information (claims about code that doesn't exist)
   - Contradictory or confusing statements
   - Generic responses with no specific repository context

3. **Negative User Feedback**
   - Thumbs down reactions on bot comments
   - User comments expressing dissatisfaction or confusion
   - Users asking for clarification or corrections
   - Users manually correcting bot responses

4. **Workflow Failures**
   - Workflow run failures visible in bot comments
   - Missing expected outputs (no comment when one was expected)
   - Timeout errors or resource limit errors

### What to Skip

- Bot comments that received positive reactions (👍, 👀 without negative follow-up)
- User comments where the conversation resolved successfully
- Workflow runs that completed successfully without errors
- Generic automated status updates ("✅ Workflow completed successfully")
- Bot responses older than 24 hours (unless related to an ongoing issue)

### Issue Format

**Issue title:** Downstream health report for [date]

**Issue body:**

> ## Downstream Repository Health Report
>
> This report covers bot activity in downstream repositories using elastic/ai-github-actions workflows for the past 24 hours.
>
> ### Monitored Repositories
>
> - elastic/integrations
> - elastic/infra-party
> - [any other discovered repos]
>
> ### Issues Found
>
> #### 1. [Repository] — [Brief description of the issue]
>
> **Location:** [Link to issue/PR comment]
> **Workflow:** [Which workflow triggered this, if known]
> **Problem:** [Detailed description of what went wrong]
> **User Impact:** [How this affected the user, if applicable]
> **Evidence:** [Quote relevant error messages, user feedback, etc.]
>
> #### 2. [Next issue...]
>
> ### Summary
>
> - Total repositories monitored: [count]
> - Total bot interactions reviewed: [count]
> - Issues found: [count]
> - Error categories: [list categories seen]
>
> ### Suggested Actions
>
> - [ ] Investigate and fix [specific error type] in [workflow name]
> - [ ] Improve [specific aspect] of bot responses
> - [ ] Follow up with users on [specific issue/PR]
> - [ ] Review and update [specific prompt/configuration]

**Guidelines:**
- Group similar issues together by type or repository
- Include direct links to all problematic comments/reviews
- Quote specific error messages or problematic response text
- Note patterns if multiple issues have the same root cause
- If no issues found, call `noop` with message "Downstream health check complete — no issues found in the past 24 hours"
