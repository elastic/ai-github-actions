# PR Review (Read-Only)

Review pull requests with read-only access. Provides feedback via comments but cannot suggest code changes or run tests.

## Usage

```yaml
- uses: your-org/ai-github-actions/workflows/pr-review/ro@v1
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Capabilities

- ✅ Read and analyze code
- ✅ Review diffs
- ✅ Provide feedback via inline comments
- ✅ Describe recommended fixes in comments
- ❌ Cannot provide GitHub suggestion blocks (clickable "Apply suggestion")
- ❌ Cannot run tests or execute commands
- ❌ Cannot modify files

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (read-only, includes PR review scripts) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |
