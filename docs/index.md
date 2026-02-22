![AI GitHub Actions Banner](assets/banner.png)

# AI GitHub Actions

AI-powered GitHub workflows for Elastic repositories.

## Recommended approach

| Feature | GitHub Agent Workflows |
| --- | --- |
| Engine | Copilot (default) or Claude |
| Install | Copy trigger YAML (recommended) |
| Guardrails | Safe-outputs framework (structured API outputs) |
| Customization | `additional-instructions`, `setup-commands`, or full shim edit |

GitHub Agent Workflows are recommended for all new deployments and ongoing maintenance.

## Workflows

- [GitHub Agent Workflows](workflows/gh-agent-workflows.md)

## Legacy

- [Claude Composite Actions (legacy)](workflows/claude-workflows.md)

## Who uses this?

### Playground (featured)

[elastic/ai-github-actions-playground](https://github.com/elastic/ai-github-actions-playground) is the reference implementation — a dedicated test-bed repository that runs the full suite of GitHub Agent Workflows. Start here to see what a fully configured repository looks like.

### Heavy users

These repositories run a broad set of workflows and serve as real-world examples of large-scale adoption:

| Repository | Notes |
| --- | --- |
| [elastic/beats](https://github.com/elastic/beats) | Large Elastic OSS repo with diverse workflow coverage |
| [elastic/integrations](https://github.com/elastic/integrations) | Large multi-package repo using multiple scheduled and event-driven workflows |

### Light users

| Repository | Notes |
| --- | --- |
| [strawgate/py-key-value](https://github.com/strawgate/py-key-value) | Small Python project using a focused set of workflows |

## More

- [Developing](developing.md)
- [Security](security.md)
- [Release process](release.md)
- [Repository README](https://github.com/elastic/ai-github-actions/blob/main/README.md)
