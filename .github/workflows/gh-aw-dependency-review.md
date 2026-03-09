---
inlined-imports: true
name: "Dependency Review"
description: "Analyze Dependabot, Renovate, and Updatecli dependency update PRs"
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
    group: "gh-aw-copilot-${{ github.workflow }}-dependency-review-${{ inputs.target-pr-number || github.event.pull_request.number }}"
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
      target-pr-number:
        description: "Explicit PR number to target (used for manual/dispatch triggers)"
        type: string
        required: false
        default: ""
      allowed-bot-users:
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      merge-ready-label:
        description: "Label to apply when all dependency updates are safe to merge without human review (e.g. 'merge-ready'). If empty, no merge-ready label is applied."
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
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
    - "dependabot[bot]"
    - "renovate[bot]"
concurrency:
  group: ${{ github.workflow }}-dependency-review-${{ inputs.target-pr-number || github.event.pull_request.number }}
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
  steps:
    - name: Pre-sanitize labels from input allowlist
      uses: actions/github-script@v7
      env:
        MERGE_READY_LABEL: ${{ inputs.merge-ready-label }}
      with:
        script: |
          const fs = require('fs');
          const outputPath = process.env.GH_AW_AGENT_OUTPUT;
          if (!outputPath || !fs.existsSync(outputPath)) {
            core.info('No GH_AW_AGENT_OUTPUT file found; skipping.');
            return;
          }
          const fixed = new Set(['needs-human-review', 'higher-risk']);
          const extra = String(process.env.MERGE_READY_LABEL || '')
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean);
          const allowed = new Set([...fixed, ...extra]);
          const doc = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
          if (!Array.isArray(doc.items)) {
            core.warning('agent output has no items array; skipping.');
            return;
          }
          let removed = 0;
          let dropped = 0;
          doc.items = doc.items.filter((item) => {
            if (item?.type !== 'add_labels' || !Array.isArray(item.labels)) {
              return true;
            }
            const before = item.labels.length;
            item.labels = item.labels
              .map((v) => String(v).trim())
              .filter((v) => v && allowed.has(v));
            removed += Math.max(0, before - item.labels.length);
            if (item.labels.length === 0) {
              dropped++;
              return false;
            }
            return true;
          });
          fs.writeFileSync(outputPath, JSON.stringify(doc));
          core.info(`Sanitized label ops: removed=${removed}, dropped_messages=${dropped}`);
strict: false
timeout-minutes: 60
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# Dependency Review Agent

Analyze dependency update pull requests (Dependabot, Renovate, Updatecli) in ${{ github.repository }}. Provide a detailed analysis comment covering changelog highlights, compatibility, risk, and ecosystem-specific checks.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ inputs.target-pr-number || github.event.pull_request.number }} — ${{ github.event.pull_request.title }}
- **PR Author**: ${{ github.actor }}

## Constraints

This workflow is read-only. You can read files, search code, run commands, and comment on PRs — but your only outputs are an analysis comment and optional labels.

## Instructions

### Step 1: Gather Context

1. Call `pull_request_read` with method `get` on PR #${{ inputs.target-pr-number || github.event.pull_request.number }} to get full PR details (author, description, branches).
2. Call `pull_request_read` with method `get_diff` to see exactly what changed.
3. Call `pull_request_read` with method `get_files` to get the list of changed files.

### Step 2: Identify and Classify Updated Dependencies

Parse the diff to identify each dependency being updated. For each dependency, extract:
- **Ecosystem**: GitHub Actions, Buildkite plugin, Go module, npm package, Python (pip/Poetry/uv), Maven/Gradle (Java), or other
- **Package name**: e.g. `actions/checkout`, `golang.org/x/net`, `express`, `requests`
- **Old version**: tag, SHA, or version before the update
- **New version**: tag, SHA, or version after the update

Classify each dependency by looking at the files changed:
- `.github/workflows/*.yml` or `.github/workflows/*.yaml` → **GitHub Actions**
- `pipeline.yml`, `.buildkite/` files → **Buildkite plugin**
- `go.mod`, `go.sum` → **Go module**
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` → **npm/Node**
- `pyproject.toml`, `requirements*.txt`, `Pipfile*`, `poetry.lock`, `uv.lock` → **Python**
- `pom.xml`, `build.gradle`, `build.gradle.kts`, `gradle.lockfile` → **Java/Kotlin (Maven/Gradle)**
- Other manifest files → classify by ecosystem

### Step 3: Analyze Each Dependency

For each updated dependency, perform the following checks:

#### 3a: Commit Verification (GitHub Actions only)

If the action reference uses a commit SHA (e.g. `uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd`):

1. Verify the commit is a verified commit by checking the GitHub API:
   ```bash
   gh api repos/{owner}/{repo}/commits/{sha} --jq '.commit.verification.verified'
   ```
1. If the commit is **not verified**, flag this prominently. Unverified commits in pinned actions are a supply-chain risk.
2. Check whether the commit SHA corresponds to a known release tag:
   ```bash
   gh api repos/{owner}/{repo}/git/matching-refs/tags --jq '.[].ref' | head -20
   ```
   Then verify the tag points to the expected SHA.

#### 3b: Changelog and Release Notes

For dependencies hosted on GitHub, fetch the release notes:
1. Fetch the release notes for the new version from the dependency's repository:
   ```bash
   gh api repos/{owner}/{repo}/releases/tags/{new_tag} --jq '.body' 2>/dev/null
   ```
1. If no release exists for the exact tag, check the latest releases:
   ```bash
   gh api repos/{owner}/{repo}/releases --jq '.[].tag_name' | head -10
   ```
3. For non-GitHub dependencies, check the package registry or changelog files in the source repo when available.
4. Summarize key changes between the old and new versions, focusing on:
   - Breaking changes or removed features
   - New required configuration or changed defaults
   - Security fixes
   - Deprecations
   - Notable new features relevant to how this repo uses the dependency

#### 3c: Usage Analysis

1. Search the repository for all places the dependency is used. The search method depends on the ecosystem:
   - **GitHub Actions**: `grep -rn '{owner}/{repo}' .github/workflows/ --include='*.yml' --include='*.yaml'`
   - **Go**: `grep -rn '{module}' --include='*.go'` (look for import statements)
   - **npm/Node**: `grep -rn "require('{package}')\|from '{package}'" --include='*.js' --include='*.ts' --include='*.mjs' --include='*.cjs'`
   - **Python**: `grep -rn "import {package}\|from {package}" --include='*.py'`
   - **Java**: `grep -rn '{groupId}' --include='*.java' --include='*.kt' --include='*.gradle' --include='*.xml'`
1. For each usage, note:
   - Which files and modules use it
   - What APIs, functions, or features are consumed
   - For GitHub Actions: what inputs are passed and outputs consumed
   - For GitHub Actions: what events trigger the workflow

3. Cross-reference the usage against the changelog:
   - Are any APIs, inputs, or features used by this repo deprecated or removed in the new version?
   - Are there breaking changes to consumed interfaces?
   - Are there new required configuration options that are not provided?

#### 3d: Testability Assessment

1. Check the trigger events for each workflow that uses the updated dependency.
2. If a workflow is **only** triggered by `push` (to main/default branch), `release`, `schedule`, or `workflow_dispatch`, it **cannot be validated by the PR itself**. Flag this as higher risk.
3. If a workflow is triggered by `pull_request` or `pull_request_target`, it can be exercised in the PR context.

#### 3e: Pin Format Check (Buildkite plugins)

For Buildkite plugin updates:
1. Check if the update moves from a SHA-pinned version to a mutable tag (higher risk).
2. Check if the update moves from one mutable tag to another mutable tag (moderate risk).
3. SHA-to-SHA or tag-to-SHA-pinned updates are preferred.

#### 3f: Ecosystem-Specific Guidance

Apply the following additional checks based on the dependency ecosystem:

**Go modules:**
- Check if this is a major version bump (e.g. v1 → v2) — Go major versions change the import path, which is a breaking change requiring code updates across the repo.
- For indirect dependency updates, note that these are transitive and generally lower risk.
- Check for `// Deprecated:` annotations in the module if accessible.

**npm / Node packages:**
- Check if this is a major semver bump — major versions typically signal breaking changes.
- Look for peer dependency conflicts that may arise from the update.
- For `devDependencies`, note that these only affect development and CI, not production.

**Python packages (pip, Poetry, uv):**
- Check if this is a major version bump — may indicate breaking API changes.
- Check for minimum Python version requirements that may have changed.
- For packages with native extensions (e.g. `numpy`, `cryptography`), note potential build or platform compatibility changes.

**Java / Kotlin (Maven, Gradle):**
- Check if this is a major version bump — may indicate breaking API changes.
- Note if the groupId or artifactId changed (dependency relocation).
- For Spring or framework dependencies, check for minimum JDK version changes.

### Step 4: Determine Labels

Based on the analysis, determine if labels should be applied:

- **`needs-human-review`**: Apply when ANY of these conditions are met:
  - A dependency update introduces breaking changes that affect this repo's usage
  - A GitHub Actions commit SHA is not verified
  - A Buildkite plugin moves from SHA-pinned to mutable tag, or between mutable tags
  - The changelog indicates breaking changes
  - A major version bump in any ecosystem (e.g. v1 → v2 in Go, major semver in npm/Python/Java)

- **`higher-risk`**: Apply when:
  - The updated dependency is used only in workflows triggered by push-to-main, release, schedule, or workflow_dispatch (cannot be validated in PR context)

${{ inputs.merge-ready-label != '' && format('- **`{0}`**: Apply when all dependency updates are safe and no issues were found — the PR can be merged without human review.', inputs.merge-ready-label) || '' }}

Only apply `needs-human-review`, `higher-risk`${{ inputs.merge-ready-label != '' && format(', and `{0}`', inputs.merge-ready-label) || '' }} labels.

### Step 5: Post Analysis Comment

Call `add_comment` on the PR with a structured analysis. Use the following format:

> ## Dependency Update Analysis
>
> **Summary**: [One-line summary of the update and overall risk assessment]
>
> ### [Dependency 1: package vOLD → vNEW]
>
> **Ecosystem**: [GitHub Actions / Go / npm / Python / Java / Buildkite / other]
>
> | Check | Result |
> | --- | --- |
> | Breaking changes | ✅ None found / ⚠️ Found (details below) |
> | Testable in PR | ✅ Yes / ⚠️ No — workflow only runs on [events] |
> | Commit verified | ✅ Yes / ⚠️ No *(GitHub Actions only)* |
> | Pin format | ✅ SHA-pinned / ⚠️ Mutable tag *(GitHub Actions / Buildkite only)* |
>
> Only include rows relevant to the dependency ecosystem. For example, "Commit verified" and "Pin format" only apply to GitHub Actions and Buildkite.
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
> [List of files/modules using this dependency and relevant APIs/inputs/outputs]
> </details>
>
> <details>
> <summary>Compatibility assessment</summary>
>
> [Analysis of whether current usage is compatible with the new version, including ecosystem-specific notes]
> </details>
>
> ### Labels Applied
> [List of labels applied and why, or "No labels applied"]

If the analysis found no issues, keep the comment concise — do not pad with unnecessary detail.

### Step 6: Apply Labels

If any labels were determined in Step 4, call `add_labels` to apply them to the PR.

${{ inputs.additional-instructions }}
