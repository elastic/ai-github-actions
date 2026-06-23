# AI GitHub Actions

@README.md
@DEVELOPING.md
@docs/upgrading.md

## Automation Runtime

Runs are executed in non-interactive CI and state is ephemeral between runs.
Persist outcomes through safe outputs (comments/issues/PRs), because uncaptured local state is lost after the run.

## GitHub Agent Workflows

See ./gh-agent-workflows

## Claude Workflows (Composite Actions)

See ./claude-workflows

## Lock Files

Files ending in `.lock.yml` in `.github/workflows/` (e.g. `gh-aw-pr-review.lock.yml`) are **auto-generated** by running `make compile` from the corresponding `.md` source file. Do not review lock files — they are machine-generated output. When a PR modifies lock files alongside their source `.md` files, review only the source `.md` files, shared fragments in `.github/workflows/gh-aw-fragments/`, and other hand-authored files (e.g. `Makefile`, `example.yml`). Lock file changes in a gh-aw version-upgrade PR are expected and do not require line-by-line review.
