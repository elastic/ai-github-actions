# Claude Workflows (Composite Actions)

Composite GitHub Actions wrapping [Claude Code](https://github.com/anthropics/claude-code-action). Consumed via `uses:` in standard GitHub Actions YAML.

> **Note:** This directory was renamed from `workflows/` to `claude-workflows/`. A symlink ensures backwards compatibility — existing `uses: elastic/ai-github-actions/workflows/...@v0` references continue to work.

## Security

> **Important:** RWX and RWXP agents can run arbitrary commands, including git commit and git push. To prevent pushes, set `contents: read` (or `contents: none`) in your workflow's `permissions:`. Prompt constraints alone are not sufficient.

> Workflows triggered by user actions should restrict who can trigger Claude. The example workflows include an `author_association` check allowing only `OWNER`, `MEMBER`, and `COLLABORATOR`. See [SECURITY.md](../SECURITY.md) for detailed guidance.

## Available Actions

### Review Agents

| Action | Description | R | W | X | Git | Push |
|--------|-------------|---|---|---|-----|------|
| [Issue Triage (RO)](issue-triage/ro/README.md) | Triage new issues (read-only) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [Issue Triage (RWX)](issue-triage/rwx/README.md) | Triage new issues (can execute tests) | ✅ | ✅ | ✅ | ✅ | ❌** |
| [PR Review (RO)](pr-review/ro/README.md) | Review PRs (suggestions only) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [PR Review (RWX)](pr-review/rwx/README.md) | Review PRs (with test execution) | ✅ | ✅ | ✅ | ✅ | ❌** |

### Assistant Agents

| Action | Description | R | W | X | Git | Push |
|--------|-------------|---|---|---|-----|------|
| [Mention in Issue (RWX)](mention-in-issue/rwx/README.md) | @claude in issues (no push) | ✅ | ✅ | ✅ | ✅ | ❌** |
| [Mention in Issue (RWXP)](mention-in-issue/rwxp/README.md) | @claude in issues (full access) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Mention in PR (RWX)](mention-in-pr/rwx/README.md) | @claude in PRs (no push) | ✅ | ✅ | ✅ | ✅ | ❌** |
| [Mention in PR (RWXP)](mention-in-pr/rwxp/README.md) | @claude in PRs (full access) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Build Failure Buildkite (RWX)](build-failure-buildkite/rwx/README.md) | Analyze Buildkite CI failures | ✅ | ✅ | ⚙️ | ✅ | ❌ |
| [Build Failure GitHub Actions (RWX)](build-failure-github-actions/rwx/README.md) | Analyze GitHub Actions failures | ✅ | ✅ | ⚙️ | ✅ | ❌ |

### Overview Agents

| Action | Description | R | W | X | Git | Push |
|--------|-------------|---|---|---|-----|------|
| [Generate Report (RO)](generate-report/ro/README.md) | Scheduled report generation | ✅ | ❌ | ⚙️ | ✅ | ❌ |
| [Project Manager (RO)](project-manager/ro/README.md) | Periodic project state reviews | ✅ | ❌ | ❌ | ✅ | ❌ |

> ✅ = default, ⚙️ = via config, ❌ = unavailable, ❌** = prompt-discouraged (enforce with `contents: read`)

## Usage

```yaml
- uses: elastic/ai-github-actions/claude-workflows/pr-review/rwx@v0
  with:
    prompt: "Review this PR"
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    github-token: ${{ github.token }}
```

### Base Action

The [base action](base/action.yml) provides full configurability:

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `prompt` | Prompt to pass to Claude | Yes | — |
| `claude-oauth-token` | Claude OAuth token | Yes | — |
| `github-token` | GitHub token for Claude | Yes | — |
| `allowed-tools` | Comma-separated allowed tools | No | `""` |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-bots` | Allowed bot usernames, or `*` for all | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See below |

### MCP Servers

All workflow actions include default MCP servers (the base action does not):

- **agents-md-generator** — Generates repository summaries from AGENTS.md. Called automatically at startup.
- **public-code-search** — Search public GitHub repos for usage patterns and reference implementations.

Override with your own:

```yaml
- uses: elastic/ai-github-actions/claude-workflows/base@v0
  with:
    prompt: "Your prompt"
    claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    mcp-servers: '{"mcpServers":{"my-server":{"type":"http","url":"https://my-server.example.com/mcp"}}}'
```
