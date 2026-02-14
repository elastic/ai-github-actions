# GitHub Agent Workflows

[GitHub Agentic Workflows](https://github.com/github/gh-aw) for Elastic repositories. All write operations go through [safe-outputs](https://github.github.io/gh-aw/reference/safe-outputs/) for security.

## Available Workflows

| Workflow | Install command | Trigger |
| --- | --- | --- |
| PR Review | `gh aw add elastic/ai-github-actions/gh-agent-workflows/pr-review` | PR opened/updated |
| Issue Triage | `gh aw add elastic/ai-github-actions/gh-agent-workflows/issue-triage` | New issues |
| Mention in Issue | `gh aw add elastic/ai-github-actions/gh-agent-workflows/mention-in-issue` | `/ai` in issues |
| Mention in PR | `gh aw add elastic/ai-github-actions/gh-agent-workflows/mention-in-pr` | `/ai` in PRs |

## Prerequisites

- [GitHub CLI](https://cli.github.com/) installed
- [gh-aw extension](https://github.com/github/gh-aw) installed: `gh extension install github/gh-aw`
- Go 1.25+ installed (for compilation)

## Quick Start

```bash
# Install a workflow
gh aw add elastic/ai-github-actions/gh-agent-workflows/pr-review

# Compile to generate the lock file
gh aw compile

# Commit both files
git add .github/workflows/pr-review.md .github/workflows/pr-review.lock.yml
git commit -m "Add PR review workflow"
git push
```

## What Gets Installed

`gh aw add` copies a slim **shim** file to `.github/workflows/` containing trigger config, engine, and a single `imports:` entry. `gh aw compile` fetches the imported prompt, tools, and safe-outputs, then generates a `.lock.yml` GitHub Actions workflow. Commit both files.

Prompt improvements propagate automatically when you recompile. Only the shim is yours to customize.

## Customization

All customization is done in the shim file (`.github/workflows/<name>.md`). Edit the frontmatter and recompile:

```bash
gh aw compile
```

### Change the AI engine or model

The default is Copilot with Claude Opus. Override in the shim's frontmatter:

```yaml
---
engine:
  id: copilot
  model: claude-sonnet-4-20250514
---
```

### Override triggers, permissions, or timeouts

Edit the shim's frontmatter to change triggers, concurrency, permissions, or timeouts:

```yaml
---
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled]
timeout-minutes: 30
---
```

### Add tools or MCP servers

Tools and network allows from imports merge additively — add your own in the shim's frontmatter:

```yaml
---
tools:
  bash: ["npm", "npx", "node"]
mcp-servers:
  my-custom-server:
    url: "https://my-server.example.com/mcp"
    allowed: ["my_tool"]
network:
  allowed:
    - "my-server.example.com"
---
```

Each workflow already includes `github` (repos, issues, pull_requests, search), `bash`, and `web-fetch` tools with `defaults` and `github` network access. Anything you add in the shim merges on top.

### Override safe outputs

Main workflow definitions override imported defaults:

```yaml
---
safe-outputs:
  add-comment:
    max: 5
---
```

### Add setup steps

Install tools the agent needs (e.g., language runtimes, build tools):

```yaml
---
steps:
  - uses: actions/setup-go@v5
    with:
      go-version: '1.23'
---
```

### Append to the prompt

Add markdown body to the shim — it's appended after the imported prompt:

```yaml
---
imports:
  - pr-review/rwx/prompt.md
engine:
  id: copilot
  model: claude-opus-4.6
on:
  pull_request:
    types: [opened, synchronize, reopened]
# ... rest of frontmatter
---

Always check for SQL injection vulnerabilities in database queries.
Focus on Go-specific issues like goroutine leaks and race conditions.
```

## Updating

```bash
# Update a specific workflow's shim to latest
gh aw update pr-review

# Update all workflows
gh aw update
```

`gh aw update` does a 3-way merge preserving your customizations. Shared imports (prompts, tools, formatting) update automatically on recompile — you only need `gh aw update` when the shim itself changes.
