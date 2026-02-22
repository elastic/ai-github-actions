---
inlined-imports: true
name: "Newbie Contributor Patrol"
description: "Review docs from a new contributor perspective and file high-impact issues"
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
  group: newbie-contributor-patrol
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
    title-prefix: "[newbie-contributor] "
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Review repository documentation from the perspective of an external contributor who knows the language/framework but is new to this project. Only file an issue for **high-impact** gaps or blockers; otherwise, report no findings.

### Data Gathering

1. Discover documentation files — scan the repository for common doc locations and read all that exist:
   - Repository root: `README.md`, `CONTRIBUTING.md`, `DEVELOPING.md`, `CHANGELOG.md`, `SECURITY.md`.
   - Documentation directories: `docs/`, `documentation/`, `doc/`.
   - Any other `.md` files in the repository root that appear to be contributor-facing.
   - Do not assume a fixed directory structure. The repository may organize docs differently.
2. Follow the quick start or recommended install path as far as possible without secrets, elevated privileges, or write access:
   - If a step requires secrets or admin privileges, stop and note whether the docs clearly warned about it.
3. Check for existing open issues that already cover the same documentation gaps.

### What to Look For

- Missing prerequisites or setup steps that would block a new contributor.
- Inconsistent instructions between the repo's own documentation files.
- Commands or file paths that do not exist in a fresh checkout.
- Required secrets, permissions, or roles that are not documented where the step appears.
- Getting-started paths that are unclear or force the contributor to guess between undocumented alternatives.

### Reporting Bar

Only report **blocking** or **high-impact** documentation issues that would prevent an external contributor from getting started. Minor wording improvements, stylistic tweaks, or optional clarifications should result in a `noop`.

### Issue Format

**Issue title:** New contributor docs review — [brief summary]

**Issue body:**

> ## Summary
> [1-2 sentence overview of the blocking issue(s)]
>
> ## Findings
>
> ### 1. [Brief description]
>
> **Where:** [doc path + section]
> **Problem:** [what is missing or incorrect]
> **Impact:** [how this blocks a new contributor]
> **Suggested fix:** [specific change]
>
> ## Suggested Actions
>
> - [ ] [Actionable checkbox for each blocking fix]

${{ inputs.additional-instructions }}
