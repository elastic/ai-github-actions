# Project Manager

Run periodic Project Manager reviews to analyze project state, identify priorities, and generate reports.

## Capabilities

- ✅ Read and analyze code
- ✅ Read-only git commands
- ✅ Query issues and PRs via `gh` CLI
- ✅ Create summary issues
- ❌ Cannot write files
- ❌ Cannot execute arbitrary commands
- ❌ Cannot commit or push changes

## Usage

See [example.yml](example.yml) for a complete workflow example.

## Features

The Project Manager workflow analyzes open issues, PRs, and recent activity, then creates a GitHub issue with a comprehensive report including:
- 🎯 Easy Pickings (PRs ready to merge, quick wins)
- 🚨 Urgent Items (blockers needing attention)
- 📋 Decisions Needed (items requiring maintainer input)
- 🔄 Stale Items (inactive issues/PRs)
- ✅ Recent Progress (merged PRs, closed issues)
- 🔧 Alignment Recommendations (patterns where AI misunderstood conventions)
- 💡 Next Steps (prioritized recommendations)

The workflow only runs if there's been sufficient activity (3+ commits, issues, or PRs) since the last PM report.

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `claude-oauth-token` | Claude OAuth token | Yes | - |
| `github-token` | GitHub token for Claude | Yes | - |
| `model` | Model to use | No | `claude-opus-4-5-20251101` |
| `allowed-tools` | Allowed tools (defaults include: read-only tools, `gh issue:*`, `gh pr:*`, MCP tools) | No | See action.yml for full default list |
| `extra-allowed-tools` | Additional allowed tools (concatenated with allowed-tools) | No | `""` |
| `additional-instructions` | Extra instructions for the prompt | No | `""` |
| `track-progress` | Track progress with visual indicators | No | `true` |
| `mcp-servers` | MCP server configuration JSON | No | See main README for MCP Servers |
| `repository-owner` | Repository owner (defaults to github.repository_owner) | No | `""` |
| `repository-name` | Repository name (defaults to github.event.repository.name) | No | `""` |

## Outputs

| Output | Description |
|--------|-------------|
| `conclusion` | The conclusion of the Claude Code run |
