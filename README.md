# AI GitHub Actions

Composite GitHub Actions that wrap the [Anthropic Claude Code Action](https://github.com/anthropics/claude-code-action) for common use cases.

## Available Actions

> **Important:** Read-write-execute (RWX) and Read-write-execute-push (RWXP) agents have access to run arbitrary commands, including git commit and git push. To prevent pushes, set `contents: read` (or `contents: none`) in the calling workflow's `permissions:` section. Without these permissions, RWX and RWXP agents may be able to push changes despite prompt constraints.

> **Security:** Workflows triggered by user actions (issue comments, new issues) should restrict who can trigger Claude. The example workflows include an `author_association` check that only allows `OWNER`, `MEMBER`, and `COLLABORATOR` to trigger Claude. This prevents anonymous users and external contributors from invoking Claude. PR review workflows rely on GitHub's built-in approval gate for external contributors instead.

### Base/Custom

| Action | Description | Read Files (R) | Write/Edit Files (W) | Execute Commands (X) | Read-Only Git | Push Changes (P) |
|--------|-------------|----------------|---------------------|----------------------|---------------|-----------------|
| [Base](base/action.yml) | Core wrapper with full configurability | ⚙️ | ⚙️ | ⚙️ | ⚙️ | ⚙️ |

### Review Agents

| Action | Description | Read Files (R) | Write/Edit Files (W) | Execute Commands (X) | Read-Only Git | Push Changes (P) |
|--------|-------------|----------------|---------------------|----------------------|---------------|-----------------|
| [Issue Triage (RO)](workflows/issue-triage/ro/README.md) | Triage and label new issues (read-only investigation) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [Issue Triage (RWX)](workflows/issue-triage/rwx/README.md) | Triage and label new issues (can execute tests, write temporary files) | ✅ | ✅ | ✅ | ✅ | ❌** |
| [PR Review (RO)](workflows/pr-review/ro/README.md) | Review pull requests (with suggestion blocks, no local file changes) | ✅ | ❌ | ❌ | ✅ | ❌ |
| [PR Review (RWX)](workflows/pr-review/rwx/README.md) | Review pull requests (with code suggestions and test execution) | ✅ | ✅ | ✅ | ✅ | ❌** |

### Assistant Agents

| Action | Description | Read Files (R) | Write/Edit Files (W) | Execute Commands (X) | Read-Only Git | Push Changes (P) |
|--------|-------------|----------------|---------------------|----------------------|---------------|-----------------|
| [Mention in Issue (RWX)](workflows/mention-in-issue/rwx/README.md) | Respond to @claude mentions on issues (can write/execute, cannot push) | ✅ | ✅ | ✅ | ✅ | ❌** |
| [Mention in Issue (RWXP)](workflows/mention-in-issue/rwxp/README.md) | Respond to @claude mentions on issues | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Mention in PR (RWX)](workflows/mention-in-pr/rwx/README.md) | Respond to @claude mentions on PRs (can write/execute, cannot push) | ✅ | ✅ | ✅ | ✅ | ❌** |
| [Mention in PR (RWXP)](workflows/mention-in-pr/rwxp/README.md) | Respond to @claude mentions on PRs | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Build Failure (Buildkite) (RWX)](workflows/build-failure-buildkite/rwx/README.md) | Analyze Buildkite CI failures and suggest fixes | ✅ | ✅ | ⚙️ | ✅ | ❌ |
| [Build Failure (GitHub Actions) (RWX)](workflows/build-failure-github-actions/rwx/README.md) | Analyze GitHub Actions workflow failures and suggest fixes | ✅ | ✅ | ⚙️ | ✅ | ❌ |

### Overview Agents

| Action | Description | Read Files (R) | Write/Edit Files (W) | Execute Commands (X) | Read-Only Git | Push Changes (P) |
|--------|-------------|----------------|---------------------|----------------------|---------------|-----------------|
| [Project Manager (RO)](workflows/project-manager/ro/README.md) | Run periodic Project Manager reviews to analyze project state | ✅ | ❌ | ❌ | ✅ | ❌ |
| [Feedback Summary (RO)](workflows/feedback-summary/ro/README.md) | Collect reactions on AI agent comments and create summary | ✅* | ❌ | ❌ | ❌ | ❌ |

### Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Available by default (included in allowed-tools) |
| ⚙️ | Available via configuration (requires `extra-allowed-tools` or custom setup) |
| ❌ | Not available |
| ✅* | Reads via GitHub API, not file system |
| ❌** | Tool is allowed, prompt discourages pushing changes. To truly restrict, set `contents: read` (or `contents: none` if you don't need repository access) in workflow permissions |

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
- **Issue Triage RWX, PR Review RWX, Mention in Issue/PR, Build Failure workflows**: All Bash commands (`Bash(*)`) are allowed by default
- **Read-Only workflows**: Bash commands are not available (except read-only git commands like `git status`, `git diff`, etc.)

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
- uses: elastic/ai-github-actions/base@v1
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
