# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## Documentation

Full documentation lives at https://elastic.github.io/ai-github-actions/.

- GitHub Agent Workflows (recommended): https://elastic.github.io/ai-github-actions/workflows/gh-agent-workflows/
- Legacy Claude Composite Actions: https://elastic.github.io/ai-github-actions/workflows/claude-workflows/
- Developing: https://elastic.github.io/ai-github-actions/developing/
- Security: https://elastic.github.io/ai-github-actions/security/
- Upgrading: https://elastic.github.io/ai-github-actions/upgrading/
- Release process: https://elastic.github.io/ai-github-actions/release/
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Overview

- GitHub Agent Workflows are the primary/recommended path and provide safe-output guardrails with configurable engines.
- Claude Composite Actions remain supported as a legacy option with RO/RWX/RWXP permission variants.

## Quick setup script

Run from the repository you want to configure (requires `gh` (authenticated via `gh auth login`), `git`, and `curl`):

````bash
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
````

By default, this installs recommended GitHub Agent Workflow triggers, adds `agentics-maintenance.yml`,
sets `COPILOT_GITHUB_TOKEN`, creates branch `ai-gh-aw-setup`, pushes it, and opens a PR. Use
`--continuous-improvement` to also install selected continuous improvement workflows.

## Who uses this?

See the [full list in the docs](https://elastic.github.io/ai-github-actions/#who-uses-this).

- **Playground**: [elastic/ai-github-actions-playground](https://github.com/elastic/ai-github-actions-playground) — reference implementation with the full workflow suite enabled.
- **Heavy users**: [elastic/beats](https://github.com/elastic/beats), [elastic/integrations](https://github.com/elastic/integrations)
- **Light users**: [strawgate/py-key-value](https://github.com/strawgate/py-key-value)

## License

MIT
