# AI GitHub Actions

Composite GitHub Actions that wrap the [Anthropic Claude Code Action](https://github.com/anthropics/claude-code-action) for common use cases.

## Available Actions

| Action | Path | Description | Documentation |
|--------|------|-------------|---------------|
| Base | `base` | Core wrapper with full configurability | See [base/action.yml](base/action.yml) |
| Issue Triage (Read-Only) | `workflows/issue-triage/ro` | Triage and label new issues (read-only investigation) | [README](workflows/issue-triage/ro/README.md) |
| Issue Triage (Read-Write-Execute) | `workflows/issue-triage/rwx` | Triage and label new issues (can execute tests, write temporary files) | [README](workflows/issue-triage/rwx/README.md) |
| PR Review (Read-Only) | `workflows/pr-review/ro` | Review pull requests (comments only, no code suggestions) | [README](workflows/pr-review/ro/README.md) |
| PR Review (Read-Write-Execute) | `workflows/pr-review/rwx` | Review pull requests (with code suggestions and test execution) | [README](workflows/pr-review/rwx/README.md) |
| Build Failure (Buildkite) | `workflows/build-failure-buildkite` | Analyze Buildkite CI failures | [README](workflows/build-failure-buildkite/README.md) |
| Build Failure (GitHub Actions) | `workflows/build-failure-github-actions` | Analyze GitHub Actions failures | [README](workflows/build-failure-github-actions/README.md) |
| Mention in Issue | `workflows/mention-in-issue` | Respond to @claude mentions on issues | [README](workflows/mention-in-issue/README.md) |
| Mention in PR | `workflows/mention-in-pr` | Respond to @claude mentions on PRs | [README](workflows/mention-in-pr/README.md) |
| Project Manager | `workflows/project-manager` | Project Manager reviews and reports | [README](workflows/project-manager/README.md) |
| Feedback Summary | `workflows/feedback-summary` | Collect and analyze AI agent feedback | [README](workflows/feedback-summary/README.md) |

## Capabilities Matrix

### Review Agents

| Action | Read Files | Write/Edit Files | Execute Commands | Read-Only Git | Push Changes |
|--------|------------|------------------|------------------|---------------|--------------|
| Issue Triage (RO) | ✅ | ❌ | ❌ | ✅ | ❌ |
| Issue Triage (RWX) | ✅ | ✅ | ✅ | ✅ | ❌** |
| PR Review (RO) | ✅ | ❌ | ❌ | ✅ | ❌ |
| PR Review (RWX) | ✅ | ✅ | ✅ | ✅ | ❌** |

### Change Agents

| Action | Read Files | Write/Edit Files | Execute Commands | Read-Only Git | Push Changes |
|--------|------------|------------------|------------------|---------------|--------------|
| Mention in Issue | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mention in PR | ✅ | ✅ | ✅ | ✅ | ✅ |
| Build Failure (Buildkite) | ✅ | ✅ | ⚙️ | ✅ | ❌ |
| Build Failure (GitHub Actions) | ✅ | ✅ | ⚙️ | ✅ | ❌ |

### Overview Agents

| Action | Read Files | Write/Edit Files | Execute Commands | Read-Only Git | Push Changes |
|--------|------------|------------------|------------------|---------------|--------------|
| Project Manager | ✅ | ❌ | ❌ | ✅ | ❌ |
| Feedback Summary | ✅* | ❌ | ❌ | ❌ | ❌ |
| Base | ⚙️ | ⚙️ | ⚙️ | ⚙️ | ⚙️ |

### Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Available by default (included in allowed-tools) |
| ⚙️ | Available via configuration (requires `extra-allowed-tools` or custom setup) |
| ❌ | Not available |
| ✅* | Reads via GitHub API, not file system |
| ❌** | Tool is allowed, prompt discourages pushing changes. To truly restrict, set `contents: none` (or `contents: read`) in workflow permissions |

## Available Tools

Claude Code has access to these tools (from the [official documentation](https://docs.anthropic.com/en/docs/claude-code/settings#tools-available-to-claude)):

| Tool | Description | Needs Permission |
|------|-------------|------------------|
| Read | Reads file contents | No |
| Write | Creates/overwrites files | Yes |
| Edit | Targeted edits to files | Yes |
| Glob | Finds files by pattern | No |
| Grep | Searches file contents | No |
| Bash | Executes shell commands | Yes |
| Task | Runs sub-agents | No |
| WebFetch | Fetches URL content | Yes |
| WebSearch | Web searches | Yes |
| NotebookEdit | Modifies Jupyter cells | Yes |

**Important:** Bash command permissions vary by workflow:
- **Issue Triage RWX, PR Review RWX, Mention in Issue/PR workflows**: All Bash commands (`Bash(*)`) are allowed by default
- **Build Failure workflows**: Bash commands must be explicitly allowed via `extra-allowed-tools` (e.g., `Bash(npm test),Bash(npm install)`)
- **Read-Only workflows**: Bash commands are not available

---

## Base Action

The core action with full configurability.

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `prompt` | Prompt to pass to Claude | Yes | - |
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `allowed-tools` | Comma-separated list of allowed tools | No | `""` |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-bots` | Allowed bot usernames, or `*` for all | No | `""` |
| `track-progress` | Track progress | No | `true` |
| `claude-args` | Additional Claude arguments | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## MCP Servers

All workflow actions (under `workflows/`) include an `mcp-servers` input with this default configuration. **Note:** The base action (`base/`) does not include default MCP servers - you must configure them manually if needed.

```json
{"mcpServers":{"agents-md-generator":{"type":"http","url":"https://agents-md-generator.fastmcp.app/mcp"},"public-code-search":{"type":"http","url":"https://public-code-search.fastmcp.app/mcp"}}}
```

- **agents-md-generator** - Generates repository summaries and AGENTS.md files
  - Claude automatically calls this tool at startup to get repository context
  - Provides essential information about codebase structure, technologies, and conventions
- **public-code-search** - Public code search

**Note**: All workflow actions instruct Claude to be extremely thorough in investigations. Claude will start by generating a repository summary using `agents-md-generator` to understand the codebase context before proceeding with the task.

### Custom MCP Configuration

Override the default MCP servers by providing your own JSON:

```yaml
- uses: your-org/ai-github-actions/base@v1
  with:
    prompt: "Your prompt"
    claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
    mcp-servers: '{"mcpServers":{"my-server":{"type":"http","url":"https://my-server.example.com/mcp"}}}'
```

## Required Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `claude-oauth-token` | `${{ secrets.CLAUDE_OAUTH_TOKEN }}` | OAuth token for Claude (configure in Settings → Secrets → Actions) |
| `github-token` | `${{ github.token }}` | Automatic GitHub token for API access |

## License

MIT
