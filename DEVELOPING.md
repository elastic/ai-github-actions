# Development Guide

This document describes specific design decisions and patterns used in this codebase that may not be immediately obvious.

## Workflow Organization

### Read-Only vs Read-Write-Execute Variants

Many workflows have two variants:
- **`ro`** (Read-Only): Investigation and analysis only, no file modifications or command execution
- **`rwx`** (Read-Write-Execute): Can write files, execute commands, run tests, but still cannot commit/push

**Why separate variants?**
- Security: Read-only workflows have fewer attack vectors
- Performance: Read-only workflows can run with fewer permissions
- Clarity: Makes capabilities explicit at the workflow level
- Flexibility: Users can choose the appropriate level of access

**Why not restrict tools instead?**
- Flexibility: Workflows need to run arbitrary test commands (npm, pytest, make, etc.) that can't be predicted
- User experience: Prompt constraints are clearer to Claude than missing tools
- Practical: Tool restrictions would require maintaining a whitelist of every possible command

**When to use `Bash(*)` vs specific commands:**
- Use `Bash(*)` when: Workflow needs to run tests, build tools, or arbitrary commands for verification
- Use specific `Bash(command:*)` patterns when: Workflow has a limited, known set of commands (e.g., read-only git commands)

**Example**: `pr-review/rwx` uses `Bash(*)` because it needs to run tests to verify code suggestions, but the prompt explicitly forbids git commit/push operations.

### GitHub Permissions

- `contents: none` - No repository access
- `contents: read` - Read-only access to the git repository
- `contents: write` - Write access to the git repository

If a workflow says "do not push" but uses `Bash(*)`, the restriction is enforced via:
1. GitHub workflow permissions (`contents: read` or `contents: none`)
2. Prompt constraints (primary enforcement)

A read-only prompt that does not properly restrict via workflow permissions may result in changes being pushed.

## MCP Server Configuration

### Default MCP Servers

**Decision**: All workflow actions (under `workflows/`) include default MCP servers, but the base action (`base/`) does not.

**Why?**
- Workflows are opinionated and benefit from repository context
- Base action is unopinionated and should be fully configurable
- Defaults reduce boilerplate for common use cases

**Default MCP servers:**
```json
{
  "mcpServers": {
    "agents-md-generator": {
      "type": "http",
      "url": "https://agents-md-generator.fastmcp.app/mcp"
    },
    "public-code-search": {
      "type": "http",
      "url": "https://public-code-search.fastmcp.app/mcp"
    }
  }
}
```

The `agents-md-generator` is called by Claude at startup (as instructed by all workflows) to get repository context. This allows us to use Claude more effectively in repositories that lack an AGENTS.md file.

## Prompt Structure

### Standard Sections

All workflow prompts follow a consistent structure:

1. **`<context>`** - Repository, issue/PR metadata
2. **`<task>`** - What Claude should do
3. **`<constraints>`** - What Claude CANNOT do (explicitly listed)
4. **`<allowed_tools>`** - Available tools (dynamically inserted)
5. **`<getting_started>`** - Initial steps (usually calls agents-md-generator)
6. **`<additional_instructions>`** - User-provided custom instructions

**Why this structure?**
- Consistency makes prompts easier to maintain
- Clear separation of concerns
- Makes it obvious what's configurable vs fixed

### Tracking Comments

All workflows include a standard footer in tracking comments:

```
---
*Comment by Claude Code* | 🚀 if perfect, 👍 if helpful, 👎 if not | Type `@claude` to interact further | [What is this?](https://ela.st/github-ai-tools)
```

**Why?**
- Provides feedback mechanism for users
- Explains what the comment is
- Consistent branding across all workflows

## Repository Context

### agents-md-generator Usage

**Decision**: All workflows instruct Claude to call `mcp__agents-md-generator__generate_agents_md` at startup.

**Why?**
- Provides essential repository context (structure, technologies, conventions)
- Helps Claude understand codebase before making decisions
- Reduces misunderstandings and improves response quality

**Pattern**: Include this in the `<getting_started>` section of every workflow prompt.

## File Naming Conventions

### Action Files

- **`action.yml`** - The composite action definition (required by GitHub Actions)
- **`example.yml`** - Example workflow showing how to use the action
- **`README.md`** - Documentation for the action

**Decision**: Every workflow action should have all three files for consistency and discoverability.

## Testing Considerations

### Workflow Testing

When testing workflows:
1. Test with minimal permissions first (read-only)
2. Verify prompt constraints are respected
3. Check that tool restrictions match documented capabilities
4. Ensure error handling works correctly

**Note**: Some workflows rely on prompt constraints rather than tool restrictions. This is intentional and documented in README files.
