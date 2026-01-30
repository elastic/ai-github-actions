# Mention in Issue (Read-Write-Execute-Push)

Respond when Claude is mentioned in issue comments. Can make code changes, run tests, commit code, push changes, and create pull requests to complete tasks. When creating pull requests, branches are automatically created by the GitHub Action.

## Usage

```yaml
- uses: elastic/ai-github-actions/workflows/mention-in-issue/rwxp@v1
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Capabilities

- ✅ Read and analyze code
- ✅ Modify files and write code
- ✅ Run tests and execute commands
- ✅ Commit code
- ✅ Push changes
- ✅ Create branches and pull requests

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
