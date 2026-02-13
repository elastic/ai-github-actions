# Development Guide

What's unique about working in this repository.

## Workflow Variants: gh-aw

Workflows are compiled to lock files using `gh-aw compile`. The lock files are stored in the `.github/workflows/` directory.

The lock files are used to deploy the workflows to the repository.

## Workflow Variants: RO / RWX / RWXP

Workflows have permission variants:

- **`ro`** — Read-only. No file writes, no command execution.
- **`rwx`** — Can write files and execute commands. Cannot commit/push.
- **`rwxp`** — Full access including commit and push.

Security enforcement: `contents: read` (or `contents: none`) in the calling workflow's `permissions:` is the real gate. Prompt constraints alone are not sufficient.

## Tool Configuration

Two inputs for tools:

- **`allowed-tools`** — Full default set. Override to replace entirely.
- **`extra-allowed-tools`** — Appended to defaults. Use this to add project-specific tools.

Use `Bash(*)` when the workflow needs arbitrary commands (tests, builds). Use `Bash(command:*)` patterns for limited, known commands (read-only git).

## Prompt Structure

All prompts use XML sections. The common ones:

- `<context>` — Repository/issue/PR metadata
- `<task>` — What to do
- `<constraints>` — What NOT to do
- `<allowed_tools>` — Available tools (dynamically inserted)
- `<additional_instructions>` — User-provided custom instructions

Beyond these, each workflow adds sections specific to its task (e.g. `<review_process>`, `<getting_started>`, `<instructions>`, `<output_format>`).

## MCP Servers

Workflow actions include default MCP servers. The base action does not.

All workflow prompts instruct Claude to call `mcp__agents-md-generator__generate_agents_md` at startup for repository context, with a fallback to manual exploration if the MCP tool fails.

## Prefer Documentation Over New Workflows

Don't create a new workflow unless you need different permissions, triggers, or tooling. Instead:

1. Write a markdown file documenting the process (e.g. `triage-cve.md`)
2. Reference it from `AGENTS.md` in the target repository
3. Use existing workflows — Claude discovers documentation automatically via `agents-md-generator`

## Releasing

See [RELEASE.md](RELEASE.md) for the full release process, version bump guidelines, and tag conventions.
