---
# Shared small-problem-fixer prompt — no `on:` field (imported by the small-problem-fixer shim)
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/workflow-edit-guardrails.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-pr.md
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
network:
  allowed:
    - defaults
    - github
---

# Small Problem Fixer

Find a small, clearly-scoped issue (or a very small set of related issues) and open a single focused PR that fixes it.

## Context

- **Repository**: ${{ github.repository }}

## Constraints

- **CAN**: Read files, search code, modify files locally, run tests and commands, create a pull request, add issue comments.
- **CANNOT**: Push directly to the repository — use `create_pull_request`.
- **Only one PR per run.**
- Only combine issues if they share the same root cause and the fix is a single small change (no broad refactors).
- Skip issues that need design decisions, large refactors, or ambiguous reproduction steps.
- If no suitable issue is found or the fix is not safe to implement quickly, call `noop` with a brief reason.

## Step 1: Gather candidates

1. Call `generate_agents_md` to get repository conventions (if it fails, continue).
2. Search for small, low-effort issues:

````text
github-search_issues: query="repo:{owner}/{repo} is:issue is:open -label:bug-hunter -\"[bug-hunter]\" (label:\"good first issue\" OR label:small OR label:\"quick fix\" OR label:\"easy\") sort:updated-asc"
````

3. If that yields no good candidates, broaden to low-comment issues:

````text
github-search_issues: query="repo:{owner}/{repo} is:issue is:open -label:bug-hunter -\"[bug-hunter]\" comments:0..2 sort:updated-asc"
````

4. For each candidate, read the full issue and comments using `issue_read` (methods `get` and `get_comments`).

## Step 2: Select a target

Choose:
- **One** best issue; or
- **Up to three** tightly related issues with a shared root cause and a single minimal fix.

Prefer issues that:
- Are clearly actionable with a small code change
- Have short or straightforward reproduction steps
- Have no active discussion indicating complex design work
- Are not duplicate reports of prior Bug Hunter issues (search open + closed Bug Hunter issues for overlap and skip duplicates).

## Step 3: Implement the fix

1. Locate the relevant code via search and file reads.
2. Make the smallest safe change that fixes the issue(s).
3. Run the most relevant targeted tests; if tests are not available, note that in the PR.
4. Commit the changes locally.

## Step 4: Create the PR

Call `create_pull_request` with:
- **Title**: concise fix summary
- **Body**: summary, linked issue(s), tests run (or not run), and any follow-ups
- **Labels**: include `small-problem-fixer` if the label exists (check with `github-get_label`); otherwise omit labels

## Step 5: Close the loop

After creating the PR, add a brief comment on each issue linking to the PR.
If no suitable issue is found, call `noop` with a brief reason.
