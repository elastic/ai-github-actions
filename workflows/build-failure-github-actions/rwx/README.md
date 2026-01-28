# Build Failure (GitHub Actions)

Analyze GitHub Actions workflow failures and suggest fixes. Can provide code suggestions and run tests to verify recommendations.

## Capabilities

- ✅ Read and analyze code
- ✅ Access workflow run logs via GitHub API
- ✅ **Write files** (test files, temporary files)
- ✅ **Execute commands** (configurable via `extra-allowed-tools`)
- ✅ Read-only git commands
- ❌ Cannot commit or push changes

## Usage

See [example.yml](example.yml) for a complete workflow example.

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (defaults include: Edit, Write, Bash(*), MCP tools) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional tools to add to the defaults | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
