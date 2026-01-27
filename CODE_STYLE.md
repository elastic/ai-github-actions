# Code Style Guide

This document describes coding standards, patterns, and best practices for scripts and logic in this codebase.

## Bash Scripts

### Error Handling

**Always use `set -e`** at the start of bash scripts to fail fast on errors.

**Check for empty values** before using them in arithmetic or string operations:

```bash
set -e
VALUE=$(command-that-might-fail)
if [ -z "$VALUE" ]; then
  echo "output=default" >> $GITHUB_OUTPUT
  exit 0
fi
# Safe to use VALUE here
```

**Why?**
- Prevents silent failures
- Avoids undefined behavior with empty variables
- Makes errors explicit and debuggable

### Example Pattern

When working with GitHub CLI commands that might fail (e.g., rate limiting, network issues):

```bash
set -e
LAST_PM_ISSUE=$(gh issue list --label "project-manager" --state open --limit 1 --json number --jq '.[0].number // ""')
echo "last_pm_issue=$LAST_PM_ISSUE" >> $GITHUB_OUTPUT
if [ -n "$LAST_PM_ISSUE" ]; then
  ISSUE_CREATED=$(gh issue view "$LAST_PM_ISSUE" --json createdAt --jq '.createdAt')
  if [ -z "$ISSUE_CREATED" ]; then
    echo "has_activity=true" >> $GITHUB_OUTPUT
    exit 0
  fi
  # Safe to use ISSUE_CREATED here
fi
```

## Script Organization

### Shared Scripts

PR review workflows share scripts located at `workflows/pr-review/scripts/`:
- `pr-comment.sh` - Add inline comments
- `pr-diff.sh` - View PR diffs with line numbers
- `pr-review.sh` - Submit review

**Path resolution**: Scripts are referenced using `${{ github.action_path }}/../scripts` to work from both `ro` and `rwx` variants.

**Decision**: Keep shared scripts in a common location rather than duplicating them.

**Pattern**: When multiple workflow variants need the same scripts, place them in a shared `scripts/` directory and reference them using relative paths from `github.action_path`.

## Tool Concatenation

### allowed-tools and extra-allowed-tools

**Pattern**: `extra-allowed-tools` is concatenated with `allowed-tools` using GitHub Actions expressions:

```yaml
claude_args: |
  ${{ format('--allowedTools {0}{1}', inputs.allowed-tools, inputs.extra-allowed-tools != '' && format(',{0}', inputs.extra-allowed-tools) || '') }}
```

**Why this pattern?**
- Allows users to extend tool lists without replacing defaults
- Maintains backward compatibility
- Handles empty strings gracefully

**Usage**: Users can add specific tools via `extra-allowed-tools` without losing default tools.

**Implementation details**:
- The format expression checks if `extra-allowed-tools` is non-empty
- If empty, it appends nothing (empty string)
- If non-empty, it prepends a comma and the value
- This ensures proper comma-separated list formatting

## GitHub Actions YAML Patterns

### Conditional Arguments

The base action uses conditional formatting for optional arguments:

```yaml
claude_args: |
  ${{ inputs.allowed-tools != '' && format('--allowedTools {0}', inputs.allowed-tools) || '' }}
  ${{ inputs.mcp-servers != '' && format('--mcp-config "{0}"', inputs.mcp-servers) || '' }}
  --model ${{ inputs.model }}
  ${{ inputs.claude-args }}
```

**Why?**
- Only includes arguments when values are provided
- Avoids passing empty strings that might cause errors
- Keeps command line clean

**Pattern**: 
- Use `!= ''` to check if a value is provided
- Use `format()` to construct the argument string
- Use `|| ''` to provide empty string fallback
- Always include arguments with defaults (like `--model`)

**Note**: The `--model` argument is always included (has a default), but optional arguments are conditionally formatted.

### workflow_dispatch Syntax

**Decision**: Use `workflow_dispatch:` (empty) not `workflow_dispatch: null`

**Why?**
- `null` is not valid YAML syntax for workflow triggers
- Empty `workflow_dispatch:` enables manual triggering without parameters
- If you need inputs, add them under `workflow_dispatch.inputs`

**Correct:**
```yaml
on:
  workflow_dispatch:
```

**Incorrect:**
```yaml
on:
  workflow_dispatch: null  # ❌ Invalid syntax
```

## Variable Naming

### GitHub Actions Inputs

Use kebab-case for input names:
- `claude-oauth-token` ✅
- `github-token` ✅
- `allowed-tools` ✅
- `extra-allowed-tools` ✅

### Environment Variables

Use UPPER_SNAKE_CASE for environment variables:
- `GITHUB_TOKEN` ✅
- `GH_TOKEN` ✅
- `PR_REVIEW_REPO` ✅

## Output Handling

### GitHub Actions Outputs

Always use `$GITHUB_OUTPUT` for setting step outputs:

```bash
echo "key=value" >> $GITHUB_OUTPUT
```

**Why?**
- Standard GitHub Actions pattern
- Works consistently across all runners
- Properly handles multi-line values

### Multi-line Outputs

For multi-line values, use heredoc or proper escaping:

```bash
cat >> $GITHUB_OUTPUT <<EOF
key<<EOF2
multi
line
value
EOF2
EOF
```
