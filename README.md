# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## Documentation

Full documentation lives at https://elastic.github.io/ai-github-actions/.

- GitHub Agent Workflows (recommended): https://elastic.github.io/ai-github-actions/workflows/gh-agent-workflows/
- Claude Composite Actions: https://elastic.github.io/ai-github-actions/workflows/claude-workflows/
- Developing: https://elastic.github.io/ai-github-actions/developing/
- Security: https://elastic.github.io/ai-github-actions/security/
- Release process: https://elastic.github.io/ai-github-actions/release/
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Overview

- GitHub Agent Workflows provide safe-output guardrails with configurable engines (Copilot or Claude).
- Claude Composite Actions provide direct Claude Code actions with RO/RWX/RWXP permission variants.

## Quick setup script

Run from the repository you want to configure (requires `gh`, `git`, and `curl`):

````bash
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
````

By default, this installs recommended GitHub Agent Workflow triggers, adds `agentics-maintenance.yml`,
sets `COPILOT_GITHUB_TOKEN`, creates branch `ai-gh-aw-setup`, pushes it, and opens a PR. Use
`--continuous-improvement` to also install selected continuous improvement workflows.

## License

MIT
