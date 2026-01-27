# AI GitHub Actions

Composite GitHub Actions that wrap the [Anthropic Claude Code Action](https://github.com/anthropics/claude-code-action) for common use cases.

## Repository Structure

```
ai-github-actions/
├── README.md
├── base/
│   └── action.yml           # Base action with full configurability
└── workflows/
    ├── issue-triage/              # Triage and label new issues
    ├── build-failure-buildkite/  # Analyze Buildkite CI failures
    ├── build-failure-github-actions/  # Analyze GitHub Actions failures
    ├── pr-review/                 # Review pull requests
    ├── mention-issue/            # Respond to @claude mentions on issues
    └── mention-pr/               # Respond to @claude mentions on PRs
```

## Available Actions

| Action | Path | Description |
|--------|------|-------------|
| [Base](#base-action) | `base` | Core wrapper with full configurability |
| [Issue Triage](#issue-triage) | `workflows/issue-triage` | Triage and label new issues |
| [Build Failure (Buildkite)](#build-failure-buildkite) | `workflows/build-failure-buildkite` | Analyze Buildkite CI failures |
| [Build Failure (GitHub Actions)](#build-failure-github-actions) | `workflows/build-failure-github-actions` | Analyze GitHub Actions failures |
| [PR Review](#pr-review) | `workflows/pr-review` | Review pull requests |
| [Mention (Issue)](#mention-issue) | `workflows/mention-issue` | Respond to @claude mentions on issues |
| [Mention (PR)](#mention-pr) | `workflows/mention-pr` | Respond to @claude mentions on PRs |

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
    github-token: ${{ github.token }}
    # Optional: allow specific tools
    allowed-tools: "Edit,Write,Bash(npm test)"
```

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
          github-token: ${{ github.token }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## Build Failure (Buildkite)

Analyze Buildkite CI build failures and suggest fixes. Claude will automatically discover the pipeline and build number from the commit SHA.

```yaml
name: Build Failure Analysis (Buildkite)
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
      - uses: your-org/ai-github-actions/workflows/build-failure-buildkite@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
          github-token: ${{ github.token }}
          buildkite-api-token: ${{ secrets.BUILDKITE_API_TOKEN }}
          # buildkite-org defaults to "elastic"
          # buildkite-pipeline auto-discovered from repo name
          # buildkite-build-number auto-discovered from commit SHA
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `buildkite-api-token` | Buildkite API token | Yes | - |
| `buildkite-org` | Buildkite organization slug | No | `"elastic"` |
| `buildkite-pipeline` | Buildkite pipeline slug (auto-discovered if not provided) | No | `""` |
| `buildkite-build-number` | Buildkite build number (auto-discovered if not provided) | No | `""` |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | Additional MCP server configuration JSON (merged with defaults) | No | `""` |

**Buildkite Auto-Discovery:**
- **Pipeline**: Automatically discovered by matching the repository name against available pipelines in the organization
- **Build Number**: Automatically discovered by searching for builds matching the commit SHA
- **Organization**: Defaults to `"elastic"` but can be overridden

---

## Build Failure (GitHub Actions)

Analyze GitHub Actions workflow failures and suggest fixes.

```yaml
name: Build Failure Analysis (GitHub Actions)
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
      - uses: your-org/ai-github-actions/workflows/build-failure-github-actions@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
          github-token: ${{ github.token }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
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
      - name: Checkout PR head branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
          fetch-depth: 0

      - name: Run Claude PR Review
        uses: your-org/ai-github-actions/workflows/pr-review@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
          github-token: ${{ github.token }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## Mention (Issue)

Respond when Claude is mentioned in issue comments.

```yaml
name: Claude Mention (Issue)
on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  issues: write

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude') && github.event.issue.pull_request == null
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/ai-github-actions/workflows/mention-issue@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
          github-token: ${{ github.token }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools | No | `""` |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

---

## Mention (PR)

Respond when Claude is mentioned in PR comments. Includes tools for managing PR review threads.

```yaml
name: Claude Mention (PR)
on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  pull-requests: write

jobs:
  respond:
    if: contains(github.event.comment.body, '@claude') && github.event.issue.pull_request != null
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/ai-github-actions/workflows/mention-pr@v1
        with:
          claude-oauth-token: ${{ secrets.CLAUDE_OAUTH_TOKEN }}
          github-token: ${{ github.token }}
```

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-sonnet-4-20250514` |
| `allowed-tools` | Allowed tools (includes PR review thread scripts) | No | `""` |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See [MCP Servers](#mcp-servers) |

**Note:** The `mention-pr` workflow includes helper scripts for managing PR review threads:
- `gh-get-review-threads.sh` - List review threads
- `gh-resolve-review-thread.sh` - Resolve a review thread
- `gh-minimize-outdated-comments.sh` - Minimize outdated comments

---

## MCP Servers

All actions include an `mcp-servers` input with this default configuration:

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
