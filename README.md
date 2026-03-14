# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## Documentation

Full documentation lives at https://elastic.github.io/ai-github-actions/.

- Elastic AI Software Factory (GitHub Agent Workflows, recommended): https://elastic.github.io/ai-github-actions/workflows/gh-agent-workflows/
- Legacy Claude Composite Actions: https://elastic.github.io/ai-github-actions/workflows/claude-workflows/
- Migration Guide (Claude → GitHub Agent Workflows): https://elastic.github.io/ai-github-actions/migration-guide/
- Developing: https://elastic.github.io/ai-github-actions/developing/
- Security: https://elastic.github.io/ai-github-actions/security/
- Upgrading: https://elastic.github.io/ai-github-actions/upgrading/
- Release process: https://elastic.github.io/ai-github-actions/release/
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Overview

- Elastic AI Software Factory (GitHub Agent Workflows) is the primary/recommended path and provides safe-output guardrails with configurable engines.
- Claude Composite Actions remain supported as a legacy option with RO/RWX/RWXP permission variants.

## Top recommended workflows

- Starter repo operations set: `pr-review`, `issue-triage`, `mention-in-issue`, `mention-in-pr`, `pr-actions-detective`
- Continuous improvement set: `bug-hunter`, `code-complexity-detector`, `code-duplication-detector`, `docs-patrol`, `newbie-contributor-patrol`, `small-problem-fixer`, `stale-issues-investigator`, `stale-issues-remediator`, `test-coverage-detector`, `breaking-change-detector`, `update-pr-body`

## Quick setup script

Run from the repository you want to configure (requires `gh` (authenticated via `gh auth login`), `git`, and `curl`):

````bash
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
````

By default, this installs recommended GitHub Agent Workflow triggers, adds `agentics-maintenance.yml`,
sets `COPILOT_GITHUB_TOKEN`, creates branch `ai-gh-aw-setup`, pushes it, and opens a PR. Use
`--continuous-improvement` to also install selected continuous improvement workflows.

## License

MIT
