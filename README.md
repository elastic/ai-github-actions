# AI GitHub Actions

Composite GitHub Actions that wrap the [Anthropic Claude Code Action](https://github.com/anthropics/claude-code-action) for common use cases.

## Repository Structure

```
ai-github-actions/
├── README.md
├── base/
│   └── action.yml           # Base action with full configurability
└── workflows/
    ├── issue-triage/        # Triage and label new issues
    ├── build-failure/       # Analyze CI failures
    ├── pr-review/           # Review pull requests
    └── mention/             # Respond to @claude mentions
```

## Available Actions

| Action | Path | Description |
|--------|------|-------------|
| [Base](#base-action) | `base` | Core wrapper with full configurability |
| [Issue Triage](#issue-triage) | `workflows/issue-triage` | Triage and label new issues |
| [Build Failure](#build-failure) | `workflows/build-failure` | Analyze CI failures |
| [PR Review](#pr-review) | `workflows/pr-review` | Review pull requests |
| [Mention](#mention) | `workflows/mention` | Respond to @claude mentions |

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

**Important:** For Bash commands, you must specify allowed commands explicitly (e.g., `Bash(npm test),Bash(npm install)`).

---

## Base Action

The core action with full configurability.

```yaml
- uses: your-org/ai-github-actions/base@v1
  with:
    prompt: "Your prompt here"
    claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
    # Optional: allow specific tools
    allowed-tools: "Edit,Write,Bash(npm test)"
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `prompt` | Prompt to pass to Claude | Yes | - |
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `allowed-tools` | Comma-separated list of allowed tools | No | `""` |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-bots` | Allowed bot usernames, or `*` for all | No | `""` |
| `track-progress` | Track progress | No | `true` |
| `claude-args` | Additional Claude arguments | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## Issue Triage

Automatically triage and label new issues.

```yaml
name: Issue Triage
on:
  issues:
    types: [opened]

permissions:
  contents: read
  issues: write

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/ai-github-actions/workflows/issue-triage@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## Build Failure

Analyze CI build failures and suggest fixes.

```yaml
name: Build Failure Analysis
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

permissions:
  contents: read
  actions: read
  issues: write
  pull-requests: write

jobs:
  analyze:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/ai-github-actions/workflows/build-failure@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## PR Review

Review pull requests for code quality, bugs, and best practices.

```yaml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/ai-github-actions/workflows/pr-review@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## Mention

Respond when Claude is mentioned in comments.

```yaml
name: Claude Mention
on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/ai-github-actions/workflows/mention@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
          # Allow Claude to edit files and run tests
          allowed-tools: "Edit,Write,Bash(npm test),Bash(npm run lint)"
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (e.g., `Edit,Write,Bash(npm test)`) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## MCP Servers

All actions include an `mcp-servers` input with this default configuration:

```json
{"mcpServers":{"agents-md-generator":{"type":"http","url":"https://agents-md-generator.fastmcp.app/mcp"},"public-code-search":{"type":"http","url":"https://public-code-search.fastmcp.app/mcp"}}}
```

- **agents-md-generator** - Generates repository summaries and AGENTS.md files
- **public-code-search** - Public code search

### Custom MCP Configuration

Override the default MCP servers by providing your own JSON:

```yaml
- uses: your-org/ai-github-actions/base@v1
  with:
    prompt: "Your prompt"
    claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
    mcp-servers: '{"mcpServers":{"my-server":{"type":"http","url":"https://my-server.example.com/mcp"}}}'
```

## Required Secrets

Configure in **Settings → Secrets → Actions**:

- `CLAUDE_OAUTH_TOKEN` - OAuth token for Claude authentication

## License

MIT
