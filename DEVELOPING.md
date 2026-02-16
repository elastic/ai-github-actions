# Development Guide

## Repository Structure

| Directory | What | Docs |
| --- | --- | --- |
| `gh-agent-workflows/` | Agentic workflow templates (shims, prompts, shared fragments) | [DEVELOPING.md](gh-agent-workflows/DEVELOPING.md) |
| `claude-workflows/` | Composite actions wrapping Claude Code | [DEVELOPING.md](claude-workflows/DEVELOPING.md) |
| `.github/workflows/` | Compiled lock files + copied shims for compilation | — |

Internal-only workflows (e.g., `gh-aw-upgrade-check.md`, `ci.yml`, `release.yml`) live directly in `.github/workflows/` and are not installable via `gh aw add`. See [gh-agent-workflows/DEVELOPING.md](gh-agent-workflows/DEVELOPING.md) for details on internal agentic workflows.

## Quick Start

```bash
make setup            # install actionlint, action-validator, gh CLI, gh-aw compiler
make compile          # sync copies + compile to lock files
make lint             # run all linters
```

## Releasing

See [RELEASE.md](RELEASE.md) for the release process, version bump guidelines, and tag conventions.
