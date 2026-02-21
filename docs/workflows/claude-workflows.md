# Legacy: Claude Composite Actions

This is the legacy workflow path. For new deployments, use [GitHub Agent Workflows](gh-agent-workflows.md).

Traditional GitHub Actions wrapping Claude Code, consumed via `uses:` in standard workflows.

> **Note:** This directory was renamed from `workflows/` to `claude-workflows/`. A symlink ensures backwards compatibility — existing `uses: elastic/ai-github-actions/claude-workflows/...@v0` references continue to work.

## Security

> **Important:** RWX and RWXP agents can run arbitrary commands, including git commit and git push. To prevent pushes, set `contents: read` (or `contents: none`) in your workflow's `permissions:`. Prompt constraints alone are not sufficient.

> Workflows triggered by user actions should restrict who can trigger Claude. The example workflows include an `author_association` check allowing only `OWNER`, `MEMBER`, and `COLLABORATOR`. See [SECURITY.md](https://github.com/elastic/ai-github-actions/blob/main/SECURITY.md) for detailed guidance.

## Available actions

### Review agents

| Action | Description | R | W | X | Git | Push |
|--------|-------------|---|---|---|-----|------|
| Issue Triage (RO) | Triage new issues (read-only) | ✅ | ❌ | ❌ | ✅ | ❌ |
| Issue Triage (RWX) | Triage new issues (can execute tests) | ✅ | ✅ | ✅ | ✅ | ❌** |
| PR Review (RO) | Review PRs (suggestions only) | ✅ | ❌ | ❌ | ✅ | ❌ |
| PR Review (RWX) | Review PRs (with test execution) | ✅ | ✅ | ✅ | ✅ | ❌** |

### Assistant agents

| Action | Description | R | W | X | Git | Push |
|--------|-------------|---|---|---|-----|------|
| Build Failure Buildkite (RWX) | Analyze Buildkite CI failures | ✅ | ✅ | ⚙️ | ✅ | ❌ |
| Build Failure GitHub Actions (RWX) | Analyze GitHub Actions failures | ✅ | ✅ | ⚙️ | ✅ | ❌ |
| Mention in Issue (RWX) | @claude in issues (no push) | ✅ | ✅ | ✅ | ✅ | ❌** |
| Mention in Issue (RWXP) | @claude in issues (full access) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mention in PR (RWX) | @claude in PRs (no push) | ✅ | ✅ | ✅ | ✅ | ❌** |
| Mention in PR (RWXP) | @claude in PRs (full access) | ✅ | ✅ | ✅ | ✅ | ✅ |

### Overview agents

| Action | Description | R | W | X | Git | Push |
|--------|-------------|---|---|---|-----|------|
| Generate Report (RO) | Scheduled report generation | ✅ | ❌ | ⚙️ | ✅ | ❌ |
| Project Manager (RO) | Periodic project state reviews | ✅ | ❌ | ❌ | ✅ | ❌ |

> ✅ = default, ⚙️ = via config, ❌ = unavailable, ❌** = prompt-discouraged (enforce with `contents: read`)

## Usage

````yaml
- uses: elastic/ai-github-actions/claude-workflows/pr-review/rwx@v0
  with:
    prompt: "Review this PR"
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
````

## Base action

The [base action](https://github.com/elastic/ai-github-actions/blob/main/claude-workflows/base/action.yml) provides full configurability:

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `prompt` | Prompt to pass to Claude | Yes | — |
| `claude-oauth-token` | Claude OAuth token | Yes | — |
| `github-token` | GitHub token for Claude | Yes | — |
| `allowed-tools` | Comma-separated allowed tools | No | `""` |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-bots` | Allowed bot usernames, or `*` for all | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See below |

## MCP servers

All workflow actions include default MCP servers (the base action does not):

- **agents-md-generator** — Generates repository summaries from AGENTS.md. Called automatically at startup.
- **public-code-search** — Search public GitHub repos for usage patterns and reference implementations.

Override with your own:

````yaml
- uses: elastic/ai-github-actions/claude-workflows/base@v0
  with:
    prompt: "Your prompt"
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-servers: '{"mcpServers":{"my-server":{"type":"http","url":"https://my-server.example.com/mcp"}}}'
````
