# Claude Composite Actions

Traditional GitHub Actions wrapping Claude Code. Consumed via `uses:` in standard workflows.

```yaml
uses: elastic/ai-github-actions/claude-workflows/pr-review/rwx@v0
```

## Key characteristics

- Claude-only execution
- Permission variants: RO, RWX, RWXP
- Configurable inputs for prompts, models, and tools

See the full catalog and configuration details in the repository: https://github.com/elastic/ai-github-actions/tree/main/claude-workflows
