# Mention in PR

Respond when Claude is mentioned in PR comments. Can make code changes, run tests, commit code, push changes, create pull requests, and resolve review threads to complete tasks. When creating pull requests, branches are automatically created by the GitHub Action. Includes tools for managing PR review threads.

## Usage

```yaml
- uses: your-org/ai-github-actions/workflows/mention-in-pr@v1
  with:
    claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

See [example.yml](example.yml) for a complete workflow example.

## PR Review Thread Tools

The `mention-in-pr` workflow includes helper scripts for managing PR review threads:
- `gh-get-review-threads.sh` - List review threads
- `gh-resolve-review-thread.sh` - Resolve a review thread

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (defaults include: Edit, Write, git commands, PR review scripts, MCP tools) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |
