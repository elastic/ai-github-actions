# PR Review (Read-Only)

Review pull requests with read-only access. Provides feedback via comments with suggestion blocks, but cannot modify files locally or run tests.

## Usage

```yaml
- uses: elastic/ai-github-actions/workflows/pr-review/ro@v1
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
- ✅ Can provide GitHub suggestion blocks (clickable "Apply suggestion")
- ❌ Cannot run tests or execute commands
- ❌ Cannot modify files

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-tools` | Allowed tools (read-only, includes PR review scripts) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `false` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

**Note on `track-progress`**: This is disabled by default for PR review because the workflow already submits a PR review. Enabling progress tracking would add a separate comment on every commit in addition to the review, creating unnecessary noise.

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
