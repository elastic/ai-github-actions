# Mention in Issue (Read-Write-Execute)

Respond when Claude is mentioned in issue comments. Can make code changes and run tests, but cannot commit or push changes. When making code changes, they are local only and cannot be pushed to the repository.

## Usage

```yaml
- uses: elastic/ai-github-actions/workflows/mention-in-issue/rwx@v1
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Capabilities

- ✅ Read and analyze code
- ✅ Modify files and write code
- ✅ Run tests and execute commands
- ❌ Cannot commit code
- ❌ Cannot push changes
- ❌ Cannot create branches or pull requests

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-tools` | Allowed tools (defaults include: Edit, Write, git commands, MCP tools) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
