# PR Review (Read-Only)

Review pull requests with read-only access. Provides feedback via comments with suggestion blocks, but cannot modify files locally or run tests.

## Usage

```yaml
- uses: elastic/ai-github-actions/claude-workflows/pr-review/ro@v0
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## Fork Support

To review pull requests from forked repositories, use the `pull_request_target` variant:

See [example-fork.yml](example-fork.yml) for a complete fork-compatible workflow example.

> [!WARNING]
> **Private repositories only.** `pull_request_target` runs in the base repository context and exposes repository secrets to fork-triggered runs. On public repositories, any external contributor can open a fork PR and trigger expensive API calls. Use the standard `pull_request` trigger for public repos — GitHub's fork approval gate ensures the workflow only runs for trusted contributors.

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
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`) | No | `balanced` |
| `minimum-severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`) | No | `low` |
| `track-progress` | Track progress with visual indicators | No | `false` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |

**Note on `track-progress`**: This is disabled by default for PR review because the workflow already submits a PR review. Enabling progress tracking would add a separate comment on every commit in addition to the review, creating unnecessary noise.

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
