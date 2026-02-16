# Issue Triage (Read-Write-Execute)

Automatically triage and label new issues with read, write, and execution capabilities. Can run tests, write temporary files for testing, but cannot commit/push code.

## Usage

```yaml
- uses: elastic/ai-github-actions/claude-workflows/issue-triage/rwx@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Capabilities

- ✅ Read and analyze code
- ✅ Search repository and git history
- ✅ Search for similar issues/PRs
- ✅ **Write files** (test files, temporary files for verification)
- ✅ **Execute commands** (all Bash commands allowed by default)
- ❌ Cannot create/checkout branches
- ❌ Cannot commit changes
- ⚠️ Do not push changes (tool is available but discouraged)

## Use Cases

- Write test files to confirm behavior
- Verify reported bugs by running tests
- Execute scripts to understand behavior
- Run linters or static analysis tools

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-tools` | Allowed tools (defaults include: Write, read-only git commands, Bash(*) for all commands, MCP tools) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
