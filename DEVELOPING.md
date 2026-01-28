# Development Guide

This document describes specific design decisions and patterns used in this codebase that may not be immediately obvious.

## Workflow Organization: RO vs RWX Pattern

Many workflows have two variants:
- **`ro`** (Read-Only): Investigation and analysis only, no file modifications or command execution
- **`rwx`** (Read-Write-Execute): Can write files, execute commands, run tests, but still cannot commit/push

**Why separate variants?**
- **Security**: Read-only workflows have fewer attack vectors
- **Performance**: Read-only workflows can run with fewer permissions
- **Clarity**: Makes capabilities explicit at the workflow level
- **Flexibility**: Users can choose the appropriate level of access

Some workflows also have an **`rwxp`** (Read-Write-Execute-Push) variant that can commit and push changes.

**Why not restrict tools instead?**
- **Flexibility**: Workflows need to run arbitrary test commands (npm, pytest, make, etc.) that can't be predicted
- **User experience**: Prompt constraints are clearer to Claude than missing tools
- **Practical**: Tool restrictions would require maintaining a whitelist of every possible command

**When to use `Bash(*)` vs specific commands:**
- Use `Bash(*)` when: Workflow needs to run tests, build tools, or arbitrary commands for verification
- Use specific `Bash(command:*)` patterns when: Workflow has a limited, known set of commands (e.g., read-only git commands)

**Example**: `pr-review/rwx` uses `Bash(*)` because it needs to run tests to verify code suggestions, but the prompt explicitly forbids git commit/push operations.

## Extra Allowed Tools Pattern

All workflow actions support two inputs for tool configuration:
- **`allowed-tools`**: The default set of tools for the workflow (can be overridden entirely)
- **`extra-allowed-tools`**: Additional tools to add to the defaults (appended to `allowed-tools`)

**Why two inputs?**
- `extra-allowed-tools` lets users add tools without replacing the carefully-curated defaults
- `allowed-tools` allows complete customization when needed
- Common use case: Adding project-specific Bash commands or custom MCP tools

**Example usage**:
```yaml
- uses: elastic/ai-github-actions/workflows/pr-review/rwx@v1
  with:
    extra-allowed-tools: "Bash(npm run lint:*),mcp__my-custom-server"
```

**Implementation**: The `claude_args` in each action concatenates the two inputs:
```yaml
claude_args: |
  ${{ format('--allowedTools {0}{1}', inputs.allowed-tools, inputs.extra-allowed-tools != '' && format(',{0}', inputs.extra-allowed-tools) || '') }}
```

## GitHub Permissions vs Prompt Constraints

If a workflow says "do not push" but uses `Bash(*)`, the restriction is enforced via:
1. **GitHub workflow permissions** (`contents: read` or `contents: none`) - Prevents actual pushes
2. **Prompt constraints** (primary enforcement) - Instructs Claude not to attempt pushes

A read-only prompt that does not properly restrict via workflow permissions may result in changes being pushed. Always set appropriate `permissions:` in the workflow file that uses the action.

## MCP Server Configuration

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

All workflow prompts instruct Claude to call `mcp__agents-md-generator__generate_agents_md` in the `<getting_started>` section.

## Prompt Structure

All workflow prompts follow a consistent structure with XML-like sections:

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

## Repository Context: agents-md-generator Usage

**Decision**: All workflows instruct Claude to call `mcp__agents-md-generator__generate_agents_md` at startup.

**Why?**
- Provides essential repository context (structure, technologies, conventions)
- Helps Claude understand codebase before making decisions
- Reduces misunderstandings and improves response quality

**Pattern**: Include this in the `<getting_started>` section of every workflow prompt.

## Releasing

### Version Tags

This repository uses semver tags with floating major version tags:

- **Semver tags** (`v1.0.0`, `v1.0.1`, `v1.2.0`) - Immutable, point to specific commits
- **Major version tags** (`v1`, `v2`) - Floating, always point to the latest semver in that major

**Why both?**
- Semver tags provide reproducibility and audit trails
- Major version tags provide convenience and automatic minor/patch updates
- Users can choose their preferred trade-off between stability and freshness

### Creating a Release

1. Ensure all changes are merged to `main`
2. Use `make release VERSION=1.0.0` or manually create and push a semver tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. The release workflow automatically:
   - Creates a GitHub release with auto-generated notes
   - Updates the `v1` tag to point to this release

### Version Bump Guidelines

- **Major** (`v1` → `v2`): Breaking changes to action inputs/outputs or behavior
- **Minor** (`v1.0` → `v1.1`): New features, new actions, non-breaking changes
- **Patch** (`v1.0.0` → `v1.0.1`): Bug fixes, documentation, prompt improvements

### User References

Users can reference actions using:
- `@v1` - Floating major version (recommended for most users)
- `@v1.0.0` - Exact semver (for reproducibility)
- `@<commit-sha>` - Full commit SHA (maximum security)

See [SECURITY.md](SECURITY.md#action-pinning) for security considerations around tag vs SHA pinning.

## Testing Considerations

When testing workflows:
1. Test with minimal permissions first (read-only)
2. Verify prompt constraints are respected
3. Check that tool restrictions match documented capabilities
4. Ensure error handling works correctly

**Note**: Some workflows rely on prompt constraints rather than tool restrictions. This is intentional and documented in README files.
