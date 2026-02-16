# PR Review (Read-Write-Execute)

Review pull requests with code suggestions and test execution capabilities. Can provide code fixes and verify them with tests.

## Usage

```yaml
- uses: elastic/ai-github-actions/claude-workflows/pr-review/rwx@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Optional: Minimize resolved review threads

To keep PR conversations focused, add the [minimize-resolved-pr-reviews](https://github.com/strawgate/minimize-resolved-pr-reviews) action after the PR review step. This requires `pull-requests: write` permissions and can be scoped to bots via `users`.

````yaml
- uses: strawgate/minimize-resolved-pr-reviews@v0
  with:
    github-token: ${{ github.token }}
    # users: "github-actions"
````

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
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-tools` | Allowed tools (includes Write/Edit, read-only git commands, Bash(*) for all commands) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | No | `balanced` |
| `minimum-severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | No | `low` |
| `track-progress` | Track progress with visual indicators | No | `false` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

**Note on `track-progress`**: This is disabled by default for PR review because the workflow already submits a PR review. Enabling progress tracking would add a separate comment on every commit in addition to the review, creating unnecessary noise.

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
