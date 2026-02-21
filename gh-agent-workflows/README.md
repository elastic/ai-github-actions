# GitHub Agent Workflows

This directory contains workflow templates and per-workflow documentation.

Full documentation and setup guides live in the docs site:
https://elastic.github.io/ai-github-actions/workflows/gh-agent-workflows/

Each workflow folder includes an `example.yml` trigger and a README covering inputs and safe outputs.

## Quick setup script

Run from the repository you want to configure:

````bash
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
````

This installs a recommended set of triggers, adds `agentics-maintenance.yml`, sets up
`COPILOT_GITHUB_TOKEN`, creates a setup branch, and opens a PR.

Default workflows:
- `pr-review`
- `issue-triage`
- `mention-in-issue`
- `mention-in-pr`
- `pr-ci-detective`

Use `--workflows` (comma-separated) to override the defaults, `--skip-secret` to set the
secret manually, `--continuous-improvement` to also install selected continuous improvement
workflows, or `--repo OWNER/REPO` when auto-detection is not available.

`--continuous-improvement` adds:
- `cli-consistency-checker`
- `ci-doctor`
- `bug-hunter`
- `bug-exterminator`
- `code-simplifier`
- `docs-drift`
- `docs-new-contributor-review`
- `small-problem-fixer`
- `stale-issues`
- `test-improvement`
- `breaking-change-detect`
- `semantic-function-clustering`
- `terminal-stylist`
- `update-pr-body`
