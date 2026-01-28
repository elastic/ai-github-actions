# PR Review (Read-Write-Execute)

Review pull requests with code suggestions and test execution capabilities. Can provide code fixes and verify them with tests.

## Usage

```yaml
- uses: elastic/ai-github-actions/workflows/pr-review/rwx@v1
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Capabilities

- ✅ Read and analyze code
- ✅ Review diffs
- ✅ Provide feedback via inline comments
- ✅ **Provide code suggestions** (via ```suggestion blocks)
- ✅ **Write files** (test files, temporary files)
- ✅ **Execute commands** (all Bash commands allowed by default)
- ❌ Cannot create/checkout branches
- ❌ Cannot commit changes
- ⚠️ Do not push changes (tool is available but discouraged)

## Use Cases

- Review PRs with actionable code suggestions
- Verify suggested fixes by running tests
- Test edge cases or scenarios

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (includes Write/Edit, read-only git commands, Bash(*) for all commands) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `false` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

**Note on `track-progress`**: This is disabled by default for PR review because the workflow already submits a PR review. Enabling progress tracking would add a separate comment on every commit in addition to the review, creating unnecessary noise.

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
