---
inlined-imports: true
name: "Code Quality Audit"
description: "Analyze code for quality issues — anti-patterns, accessibility violations, performance problems, best-practices deviations — and file a structured report"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/ensure-full-history.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/pick-three-keep-many.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/network-ecosystems.md
  - gh-aw-fragments/code-quality-audit.md
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
        description: "Domain-specific audit criteria — what to look for, what to skip, and how to evaluate findings. This is the core of the audit and should define the categories, severity standards, and evidence expectations for the specific quality dimension being audited."
        type: string
        required: true
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
      title-prefix:
        description: "Title prefix for created issues (e.g. '[react-accessibility]')"
        type: string
        required: true
      severity-threshold:
        description: "Minimum severity to include in the report. 'high' = only report issues with clear user impact or correctness problems. 'medium' (default) = also include issues that degrade quality or maintainability. 'low' = also include minor deviations from best practices."
        type: string
        required: false
        default: "medium"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-code-quality-audit
  cancel-in-progress: true
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, labels, actions]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Validate severity threshold
    env:
      SEVERITY_THRESHOLD: ${{ inputs.severity-threshold }}
    run: |
      case "$SEVERITY_THRESHOLD" in
        high|medium|low) ;;
        *)
          echo "Invalid severity-threshold: '$SEVERITY_THRESHOLD'. Expected one of: high, medium, low."
          exit 1
          ;;
      esac
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

### Data Gathering

1. Understand the project:
   - Read `README.md`, `CONTRIBUTING.md`, `DEVELOPING.md`, and any docs directory.
   - Read `package.json`, `go.mod`, `pyproject.toml`, or equivalent to identify the tech stack and versions.
   - Skim the directory structure to understand the codebase layout.

2. Use the **Pick Three, Keep Many** pattern for the audit:
   - Spawn 3 `general-purpose` sub-agents, each auditing from a different angle as defined in the **Audit Criteria** section below.
   - Each sub-agent prompt must include: the full audit criteria, the tech stack info, relevant file paths, and the severity threshold.
   - Each sub-agent should return all findings that meet the severity threshold, with specific file paths, line numbers, and code snippets.
   - Wait for all sub-agents to complete, then merge and deduplicate.

3. Check for duplicates:
   - Read `/tmp/previous-findings.json` for issues already filed by this agent.
   - Search open issues: `repo:{owner}/{repo} is:issue is:open in:title "${{ inputs.title-prefix }}"`.
   - Drop any finding that closely matches an existing open issue.

### Labeling

- If a label matching the title prefix (without brackets) exists (check with `github-get_label`), include it in the `create_issue` call; otherwise, rely on the `${{ inputs.title-prefix }}` title prefix only.

## Audit Criteria

${{ inputs.additional-instructions }}
