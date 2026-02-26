---
inlined-imports: true
name: "Dependency Review"
description: "Analyze Dependabot and Renovate PRs for GitHub Actions and Buildkite dependency updates"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-pr.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-dependency-review-${{ github.event.pull_request.number }}"
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
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
    - "dependabot[bot]"
    - "renovate[bot]"
concurrency:
  group: dependency-review-${{ github.event.pull_request.number }}
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
safe-outputs:
  activation-comments: false
  add-labels:
    max: 3
    allowed:
      - "needs-human-review"
      - "higher-risk"
strict: false
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

# Dependency Review Agent

Analyze dependency update pull requests (Dependabot, Renovate) in ${{ github.repository }} and provide a detailed analysis comment covering security, compatibility, and risk.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} — ${{ github.event.pull_request.title }}
- **PR Author**: ${{ github.actor }}

## Constraints

This workflow is read-only. You can read files, search code, run commands, and comment on PRs — but your only outputs are an analysis comment and optional labels.

## Instructions

### Step 1: Gather Context

1. Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.
2. Call `pull_request_read` with method `get` on PR #${{ github.event.pull_request.number }} to get full PR details (author, description, branches).
3. Call `pull_request_read` with method `get_diff` to see exactly what changed.
4. Call `pull_request_read` with method `get_files` to get the list of changed files.

### Step 2: Identify Updated Dependencies

Parse the diff to identify each dependency being updated. For each dependency, extract:
- **Type**: GitHub Action, Buildkite plugin, or other
- **Source repository**: e.g. `actions/checkout`, `docker/build-push-action`
- **Old version**: tag, SHA, or version before the update
- **New version**: tag, SHA, or version after the update

If the PR does not update any GitHub Actions or Buildkite plugin dependencies, call `noop` with message "PR does not update GitHub Actions or Buildkite dependencies; nothing to analyze" and stop.

### Step 3: Analyze Each Dependency

For each updated dependency, perform the following checks:

#### 3a: Commit Verification (GitHub Actions only)

If the action reference uses a commit SHA (e.g. `uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd`):

1. Verify the commit is a verified commit by checking the GitHub API:
   ```bash
   gh api repos/{owner}/{repo}/commits/{sha} --jq '.commit.verification.verified'
   ```
2. If the commit is **not verified**, flag this prominently. Unverified commits in pinned actions are a supply-chain risk — see [Imposter Commits in CI/CD](https://www.chainguard.dev/unchained/what-the-fork-imposter-commits-in-github-actions-and-ci-cd).
3. Check whether the commit SHA corresponds to a known release tag:
   ```bash
   gh api repos/{owner}/{repo}/git/matching-refs/tags --jq '.[].ref' | head -20
   ```
   Then verify the tag points to the expected SHA.

#### 3b: Changelog and Release Notes

1. Fetch the release notes for the new version from the dependency's repository:
   ```bash
   gh api repos/{owner}/{repo}/releases/tags/{new_tag} --jq '.body' 2>/dev/null
   ```
2. If no release exists for the exact tag, check the latest releases:
   ```bash
   gh api repos/{owner}/{repo}/releases --jq '.[].tag_name' | head -10
   ```
3. Summarize key changes between the old and new versions, focusing on:
   - Breaking changes or removed features
   - New required inputs or changed defaults
   - Security fixes
   - Notable new features relevant to how this repo uses the action

#### 3c: Usage Analysis

1. Search the repository for all places the dependency is used:
   ```bash
   grep -rn '{owner}/{repo}' .github/workflows/ --include='*.yml' --include='*.yaml'
   ```
2. For each usage, note:
   - Which workflow file and job uses it
   - What inputs are passed to it
   - What outputs are consumed from it
   - What events trigger the workflow (push, pull_request, schedule, release, etc.)

3. Cross-reference the usage against the changelog:
   - Are any inputs used by this repo deprecated or removed in the new version?
   - Are any outputs consumed by this repo changed in the new version?
   - Are there new required inputs that are not provided?

#### 3d: Testability Assessment

1. Check the trigger events for each workflow that uses the updated dependency.
2. If a workflow is **only** triggered by `push` (to main/default branch), `release`, `schedule`, or `workflow_dispatch`, it **cannot be validated by the PR itself**. Flag this as higher risk.
3. If a workflow is triggered by `pull_request` or `pull_request_target`, it can be exercised in the PR context.

#### 3e: Pin Format Check (Buildkite plugins)

For Buildkite plugin updates:
1. Check if the update moves from a SHA-pinned version to a mutable tag (higher risk).
2. Check if the update moves from one mutable tag to another mutable tag (moderate risk).
3. SHA-to-SHA or tag-to-SHA-pinned updates are preferred.

### Step 4: Determine Labels

Based on the analysis, determine if labels should be applied:

- **`needs-human-review`**: Apply when ANY of these conditions are met:
  - A GitHub Action update introduces breaking input/output changes that affect this repo's usage
  - A commit SHA is not verified
  - A Buildkite plugin moves from SHA-pinned to mutable tag, or between mutable tags
  - The changelog indicates breaking changes

- **`higher-risk`**: Apply when:
  - The updated dependency is used only in workflows triggered by push-to-main, release, schedule, or workflow_dispatch (cannot be validated in PR context)

Only apply `needs-human-review` and `higher-risk` labels.

### Step 5: Post Analysis Comment

Call `add_comment` on the PR with a structured analysis. Use the following format:

> ## Dependency Update Analysis
>
> **Summary**: [One-line summary of the update and overall risk assessment]
>
> ### [Dependency 1: owner/repo vOLD → vNEW]
>
> | Check | Result |
> | --- | --- |
> | Commit verified | ✅ Yes / ⚠️ No |
> | Breaking changes | ✅ None found / ⚠️ Found (details below) |
> | Testable in PR | ✅ Yes / ⚠️ No — workflow only runs on [events] |
> | Pin format | ✅ SHA-pinned / ⚠️ Mutable tag |
>
> <details>
> <summary>Changelog highlights (vOLD → vNEW)</summary>
>
> [Key changes from release notes]
> </details>
>
> <details>
> <summary>Usage in this repository</summary>
>
> [List of workflows/jobs using this dependency and relevant inputs/outputs]
> </details>
>
> <details>
> <summary>Compatibility assessment</summary>
>
> [Analysis of whether current usage is compatible with the new version]
> </details>
>
> ### Labels Applied
> [List of labels applied and why, or "No labels applied"]

If the analysis found no issues, keep the comment concise — do not pad with unnecessary detail.

### Step 6: Apply Labels

If any labels were determined in Step 4, call `add_labels` to apply them to the PR.

${{ inputs.additional-instructions }}
