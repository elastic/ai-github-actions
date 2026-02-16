# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## GitHub Agent Workflows (Recommended)

[GitHub Agentic Workflows](https://github.com/github/gh-aw) with safe-output guardrails. Engine and model are configurable per workflow.

```bash
gh aw add elastic/ai-github-actions/gh-agent-workflows/pr-review.md
gh aw compile
```

| Workflow | Trigger | Description |
| --- | --- | --- |
| PR Review | PR opened/updated | Automated code review with inline comments |
| Issue Triage | New issues | Investigate and provide implementation plans |
| Mention in Issue | `/ai` command | Answer questions, debug, create PRs |
| Mention in PR | `/ai` command | Review, fix code, push changes |
| Docs Drift | Weekday schedule | Detect code changes needing doc updates |

See **[gh-agent-workflows/](gh-agent-workflows/)** for install commands, customization, and updating.

## Composite Actions (Claude Code)

Traditional GitHub Actions wrapping [Claude Code](https://github.com/anthropics/claude-code-action). Consumed via `uses:` in standard YAML workflows.

```yaml
uses: elastic/ai-github-actions/claude-workflows/pr-review/rwx@v0
```

Includes review agents, assistant agents, build failure analyzers, and report generators — each with configurable permission levels (RO, RWX, RWXP).

See **[claude-workflows/](claude-workflows/)** for the full catalog and configuration.

> **Note:** `claude-workflows/` was renamed from `workflows/`. A symlink ensures backwards compatibility.

## License

MIT
