![AI GitHub Actions Banner](assets/banner.png)

# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## Recommended approach

| Feature | GitHub Agent Workflows | Legacy Claude Composite Actions |
| --- | --- | --- |
| Engine | Copilot (default) or Claude | Claude only |
| Install | Copy trigger YAML (recommended) | Copy `example.yml` to `.github/workflows/` |
| Guardrails | Safe-outputs framework (structured API outputs) | Read-only/RWX/RWXP variants via permissions |
| Customization | `additional-instructions`, `setup-commands`, or full shim edit | Edit YAML directly, adjust composite action inputs |

GitHub Agent Workflows are recommended for all new deployments and ongoing maintenance.

## Workflows

- [GitHub Agent Workflows](workflows/gh-agent-workflows.md)

## Legacy

- [Claude Composite Actions (legacy)](workflows/claude-workflows.md)

## More

- [Developing](developing.md)
- [Security](security.md)
- [Release process](release.md)
- [Repository README](https://github.com/elastic/ai-github-actions/blob/main/README.md)
