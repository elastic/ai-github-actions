# Development Guide

## Repository Structure

| Directory | What | Docs |
| --- | --- | --- |
| `.github/workflows/` | Workflow `gh-aw-*.md` sources, compiled `gh-aw-*.lock.yml` files, trigger copies, fragments | [DEVELOPING.md](gh-agent-workflows/DEVELOPING.md) |
| `gh-agent-workflows/` | Trigger `.yml` examples/dogfood, shared fragments, consumer docs | [DEVELOPING.md](gh-agent-workflows/DEVELOPING.md) |
| `claude-workflows/` | Composite actions wrapping Claude Code | [DEVELOPING.md](claude-workflows/DEVELOPING.md) |

Internal-only workflows (e.g., `gh-aw-upgrade-check.md`, `ci.yml`, `release.yml`) also live in `.github/workflows/`. See [gh-agent-workflows/DEVELOPING.md](gh-agent-workflows/DEVELOPING.md) for the full architecture.

## Quick Start

```bash
make setup            # install actionlint, action-validator, gh CLI, gh-aw compiler
make compile          # sync triggers + compile to lock files
make lint             # run all linters
```

## Releasing

See [RELEASE.md](RELEASE.md) for the release process, version bump guidelines, and tag conventions.
