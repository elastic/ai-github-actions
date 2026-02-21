# Developing

## Repository structure

| Directory | What | Docs |
| --- | --- | --- |
| `.github/workflows/` | Workflow `gh-aw-*.md` sources, compiled `gh-aw-*.lock.yml` files, trigger copies, fragments | https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/DEVELOPING.md |
| `gh-agent-workflows/` | Per-workflow READMEs, `example.yml` triggers, and optional `dogfood-with.yml` overrides | https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/DEVELOPING.md |
| `claude-workflows/` | Composite actions wrapping Claude Code | https://github.com/elastic/ai-github-actions/blob/main/claude-workflows/DEVELOPING.md |

Internal-only workflows (e.g., `upgrade-check.md`, `workflow-patrol.md`, `ci.yml`, `release.yml`) also live in `.github/workflows/`. Published workflows use the `gh-aw-` prefix; internal-only ones omit it.

## Quick start

```bash
make setup            # install actionlint, action-validator, gh CLI, gh-aw compiler
make compile          # sync triggers + compile to lock files
make lint             # run all linters
```

## Releasing

See [Release process](release.md) and the full guide in https://github.com/elastic/ai-github-actions/blob/main/RELEASE.md.
