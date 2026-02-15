# Developing Claude Workflows

## Permission Variants

Each workflow has permission variants:

- **`ro`** — Read-only. No file writes, no command execution.
- **`rwx`** — Can write files and execute commands. Cannot commit/push.
- **`rwxp`** — Full access including commit and push.

**Security enforcement:** `contents: read` (or `contents: none`) in the calling workflow's `permissions:` is the real gate. Prompt constraints alone are not sufficient.

## Tool Configuration

Two inputs control Claude's available tools:

- **`allowed-tools`** — Full default set. Override to replace entirely.
- **`extra-allowed-tools`** — Appended to defaults. Use this to add project-specific tools.

Use `Bash(*)` when the workflow needs arbitrary commands (tests, builds). Use `Bash(command:*)` patterns for limited, known commands (read-only git).

### Available Tools

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

## Prompt Structure

All prompts use XML sections:

- `<context>` — Repository/issue/PR metadata
- `<task>` — What to do
- `<constraints>` — What NOT to do
- `<allowed_tools>` — Available tools (dynamically inserted)
- `<additional_instructions>` — User-provided custom instructions

Each workflow adds task-specific sections (e.g., `<review_process>`, `<output_format>`).

## MCP Servers

All workflow actions include default MCP servers. The base action does not.

Prompts instruct Claude to call `mcp__agents-md-generator__generate_agents_md` at startup for repository context, with a fallback to manual exploration if it fails.

## Prefer Documentation Over New Workflows

Don't create a new workflow unless you need different permissions, triggers, or tooling. Instead:

1. Write a markdown file documenting the process (e.g., `triage-cve.md`)
2. Reference it from `AGENTS.md` in the target repository
3. Use existing workflows — Claude discovers documentation automatically via `agents-md-generator`

### When to Create a New Workflow

- Fundamentally different permissions (e.g., push vs no-push)
- A different trigger mechanism (e.g., scheduled vs on-demand)
- Specialized tooling or MCP servers not in existing workflows

### When to Use Documentation Instead

- Customize how Claude handles a specific task type (e.g., CVE triage, security reviews)
- Add domain-specific guidance or checklists
- Improve context for existing workflows
- Document runbooks or processes
