# Code Style Guide

This document describes unique patterns and conventions used in this codebase that may not be immediately obvious.

## Shared Scripts Path Resolution

When workflows share scripts (like `pr-review/ro` and `pr-review/rwx`), scripts are placed in a parent `scripts/` directory and referenced using:

```yaml
Bash(${{ github.action_path }}/../scripts/script-name.sh:*)
```

This allows both `ro` and `rwx` variants to reference the same scripts from their respective `action.yml` files.

**When scripts are workflow-specific** (not shared), place them in `workflows/<workflow>/scripts/` and reference as:

```yaml
Bash(${{ github.action_path }}/scripts/script-name.sh:*)
```

## Tool Concatenation Pattern

The `extra-allowed-tools` input is concatenated with `allowed-tools` using GitHub Actions expressions:

```yaml
claude_args: |
  ${{ format('--allowedTools {0}{1}', inputs.allowed-tools, inputs.extra-allowed-tools != '' && format(',{0}', inputs.extra-allowed-tools) || '') }}
```

This pattern:
- Allows users to extend tool lists without replacing defaults
- Handles empty strings gracefully (no trailing comma)
- Maintains backward compatibility

## Conditional Arguments in Base Action

The base action uses conditional formatting for optional arguments:

```yaml
claude_args: |
  ${{ inputs.allowed-tools != '' && format('--allowedTools {0}', inputs.allowed-tools) || '' }}
  ${{ inputs.mcp-servers != '' && format('--mcp-config "{0}"', inputs.mcp-servers) || '' }}
  --model ${{ inputs.model }}
  ${{ inputs.claude-args }}
```

Only include arguments when values are provided. Arguments with defaults (like `--model`) are always included.

## Environment Variables for Scripts

Scripts expect specific environment variables set by the composite action:

**PR Review scripts** (`workflows/pr-review/scripts/`):
- `PR_REVIEW_REPO` - Repository (owner/repo)
- `PR_REVIEW_PR_NUMBER` - Pull request number
- `PR_REVIEW_HEAD_SHA` - Expected head SHA (for race condition detection)
- `PR_REVIEW_COMMENTS_DIR` - Directory for storing comment data
- `PR_SCRIPTS` - Path to scripts directory

**Mention in PR scripts** (`workflows/mention-in-pr/scripts/`):
- `MENTION_REPO` - Repository (owner/repo)
- `MENTION_PR_NUMBER` - Pull request number
- `MENTION_SCRIPTS` - Path to scripts directory

**Feedback Summary scripts** (`workflows/feedback-summary/scripts/`):
- Scripts are executed directly by the action, not via Bash tool

Set these in the `env:` section of the composite action step.

## Prompt Structure Convention

All workflow prompts follow a consistent structure with XML-like sections:

1. `<context>` - Repository, issue/PR metadata
2. `<task>` - What Claude should do
3. `<constraints>` - What Claude CANNOT do (explicitly listed)
4. `<allowed_tools>` - Available tools (dynamically inserted)
5. `<getting_started>` - Initial steps (usually calls agents-md-generator)
6. `<additional_instructions>` - User-provided custom instructions

This structure ensures consistency and makes it obvious what's configurable vs fixed.

## Tracking Comment Footer

All workflows include a standard footer in tracking comments:

```

---
*Comment by Claude Code* | 🚀 if perfect, 👍 if helpful, 👎 if not | Type `@claude` to interact further | [What is this?](https://ela.st/github-ai-tools)
```

This footer is documented in the prompt's `<tracking_comment>` or `<response_footer>` section.


## File Naming Convention

Every workflow action should have three files:
- **`action.yml`** - The composite action definition (required by GitHub Actions)
- **`example.yml`** - Example workflow showing how to use the action
- **`README.md`** - Documentation for the action

This ensures consistency and discoverability across all workflows.
