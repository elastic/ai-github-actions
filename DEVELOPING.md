# Development Guide

## Repository Structure

| Directory | What | Docs |
| --- | --- | --- |
| `gh-agent-workflows/` | Agentic workflow templates (shims, prompts, shared fragments) | [DEVELOPING.md](gh-agent-workflows/DEVELOPING.md) |
| `claude-workflows/` | Composite actions wrapping Claude Code | [DEVELOPING.md](claude-workflows/DEVELOPING.md) |
| `.github/workflows/` | Compiled lock files + symlinks for local dev | — |

## Quick Start

```bash
make setup            # install all dev tools
make compile          # sync templates + compile to lock files
make lint             # run all linters
```

## Releasing

See [RELEASE.md](RELEASE.md) for the release process, version bump guidelines, and tag conventions.
