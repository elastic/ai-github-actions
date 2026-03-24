---
inlined-imports: true
name: "Update PR Body"
description: "Keep pull request bodies in sync with the code changes on every commit"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/safe-output-update-pr.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
  concurrency:
    group: "gh-aw-copilot-${{ github.workflow }}-update-pr-body-${{ github.event.pull_request.number }}"
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
        description: "Allowed bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      edit-accuracy:
        description: "How aggressively to fix factual inaccuracies in the PR body. 'high' = fix everything that could mislead, 'low' = fix only clear-cut inaccuracies, 'none' = do not change accuracy-related content"
        type: string
        required: false
        default: "low"
      edit-completeness:
        description: "How aggressively to add missing information about significant changes. 'high' = proactively add any notable missing detail, 'low' = add only major omissions that would block reviewer understanding, 'none' = do not add content"
        type: string
        required: false
        default: "low"
      edit-format:
        description: "How aggressively to improve markdown formatting and structure. 'high' = apply best-practice formatting throughout, 'low' = fix broken or unreadable formatting only, 'none' = do not touch formatting"
        type: string
        required: false
        default: "none"
      edit-style:
        description: "How aggressively to improve writing style and clarity. 'high' = rewrite for clarity, conciseness, and professionalism, 'low' = fix only confusing or misleading phrasing, 'none' = do not touch style"
        type: string
        required: false
        default: "none"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-update-pr-body-${{ github.event.pull_request.number }}
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  messages:
    footer: "${{ inputs.messages-footer || format('---\nThe body of this PR [is automatically managed](https://ela.st/github-ai-tools) by the [{0} workflow]({{run_url}}).', github.workflow) }}"
timeout-minutes: 30
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# PR Body Update Agent

Keep the pull request body in sync with the actual state of the code changes in ${{ github.repository }}.

## Context

- **Repository**: ${{ github.repository }}
- **PR**: #${{ github.event.pull_request.number }} — ${{ github.event.pull_request.title }}
- **Runtime-managed footer override input**: `${{ inputs.messages-footer }}`
- **Default runtime footer text (used when no override is provided)**:

```text
---
The body of this PR is automatically managed by the workflow runtime.
```

## Edit Level Configuration

The following edit levels are configured for this run. Each dimension is independent.

| Dimension | Level | Meaning |
| --- | --- | --- |
| **accuracy** | `${{ inputs.edit-accuracy }}` | How aggressively to fix content that misrepresents the code changes |
| **completeness** | `${{ inputs.edit-completeness }}` | How aggressively to add information about significant changes not yet mentioned |
| **format** | `${{ inputs.edit-format }}` | How aggressively to improve markdown formatting and structure |
| **style** | `${{ inputs.edit-style }}` | How aggressively to improve writing clarity, conciseness, and tone |

Level semantics:

- **`high`** — apply the agent's best judgment; proactively improve this dimension throughout the body
- **`low`** — make only conservative fixes for clear problems; do not restructure or rewrite
- **`none`** — do not touch this dimension at all; leave it exactly as the author wrote it

## Objective

Evaluate the PR body against all configured edit dimensions. Apply changes only where a dimension's level permits action. Always make the minimal edit needed within what each level allows.

## Instructions

### Step 1: Gather Context

1. Call `pull_request_read` with method `get` on PR #${{ github.event.pull_request.number }} to get the full PR details — current body, commits, and file list.
2. Call `pull_request_read` with method `get_files` to get the list of changed files.
3. If the PR description references issues (e.g., "Fixes #123", "Closes #456"), call `issue_read` with method `get` on each linked issue to understand the original motivation.

### Step 2: Analyze the Diff

Run `git log --oneline ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}` to see the commit history, then read the actual diff:

```bash
git diff --stat ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }}
```

For key changed files, read relevant sections to understand the scope and nature of the changes.

### Step 3: Evaluate Each Dimension

Assess the PR body across each configured dimension. Use the level to determine how much action is warranted.

#### Accuracy (`${{ inputs.edit-accuracy }}`)

- **`high`**: Fix anything that could mislead a reviewer — incorrect behavior descriptions, wrong file/function names, outdated scope, or wrong details about what the change does.
- **`low`**: Fix only clear-cut inaccuracies — statements that are plainly wrong and would directly confuse a reviewer. Leave ambiguous or incomplete-but-not-wrong content alone.
- **`none`**: Do not change accuracy-related content. Skip this dimension entirely.

#### Completeness (`${{ inputs.edit-completeness }}`)

- **`high`**: Proactively add any notable missing detail — new APIs, config options, renamed symbols, important side effects, or anything a reviewer would want to know.
- **`low`**: Add content only for major omissions — a new public API, endpoint, configuration option, or workflow that was added/removed/renamed and is entirely absent from the body. Do not add minor details.
- **`none`**: Do not add any content, even if significant changes are undocumented. Skip this dimension entirely.

#### Format (`${{ inputs.edit-format }}`)

- **`high`**: Apply best-practice markdown formatting throughout — consistent headers, lists, code blocks, and structure that improves readability.
- **`low`**: Fix only broken or unreadable formatting — malformed markdown that renders incorrectly or makes the body hard to parse. Do not restructure content that is already readable.
- **`none`**: Do not touch formatting. Leave the body structure exactly as the author wrote it. Skip this dimension entirely.

#### Style (`${{ inputs.edit-style }}`)

- **`high`**: Rewrite for clarity, conciseness, and professionalism — remove filler, tighten sentences, and improve tone throughout.
- **`low`**: Fix only confusing or misleading phrasing — sentences that are so unclear a reviewer would misunderstand the intent. Do not rewrite clear prose.
- **`none`**: Do not touch writing style or phrasing. Skip this dimension entirely.

### Step 4: Identify Changes Needed

Based on your analysis, compile the full list of changes warranted across all non-`none` dimensions. Group them by dimension.

Before proposing body changes, normalize footer content:

- Identify and remove any existing footer block(s) that match either:
  - the configured runtime-managed footer override input (when present), or
  - the default runtime footer text above.
- If the PR body contains repeated copies of that same footer, remove all copies from the authored content you are editing.
- Treat this cleanup as mechanical deduplication, not a style/format rewrite.

Do **not** propose changes when:

- The dimension level is `none`
- The level is `low` and the issue is minor (style preference, slight improvement, optional detail)
- An update would erase useful context (motivation, design decisions, issue links) the author provided
- The body is a reasonable high-level summary even if some details differ

**Never willingly add any of the following to the PR body** (even in `high` mode):

- Commit counts, file counts, or insertion/deletion statistics (e.g., "2 commits, 143 files changed, 12,613 insertions")
- Scope or size summaries — the reviewer can see these in the GitHub UI
- Lists of every file changed — link to relevant code instead
- Boilerplate sections with no substantive content (e.g., empty "Testing" or "Screenshots" headers)
- Agent attribution or footers — the runtime handles this

### Step 5: Update or Noop

**If any changes are warranted:**

Call `update_pull_request` **exactly once** with a `replace` operation to write a body that applies all warranted changes. You may only call this tool once per run — additional calls will be rejected by validation. The updated body must:

- Apply only the changes identified in Step 4 — do not make unplanned edits
- Preserve the original structure, formatting, and wording of sections untouched by warranted changes
- Preserve the original motivation and context (including issue links like `Fixes #N`)
- Respect the level boundaries — a `low`-level edit must not silently expand into a `high`-level rewrite

**If no changes are warranted:**

Call `noop` with a brief message summarising why each dimension required no update.

${{ inputs.additional-instructions }}
