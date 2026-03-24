# Product Manager Impersonator

Propose well-researched new feature ideas as GitHub issues from a configurable persona and scope.

## How it works

Reviews the codebase, recent activity, and existing issues to propose a single new feature idea that is customer-aligned, grounded in the existing code, and tractable. Each idea includes a rough implementation sketch and a "why it won't be that hard" rationale. Only files an issue when a genuinely useful, non-duplicate idea is found — most runs end with `noop`.

Use the `persona` input to adopt a domain-specific perspective (e.g., SRE, security analyst, search engineer) and the `idea-size` input to control whether the idea is scoped as a quick win or a multi-sprint effort.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/product-manager-impersonator/example.yml \
  -o .github/workflows/product-manager-impersonator.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `persona` | Persona description for domain-specific ideas (e.g., `a seasoned SRE who lives in logs and traces`) | No | `""` |
| `idea-size` | Scope framing: `small` (quick iterative win) or `medium` (1–2 sprint effort) | No | `"small"` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `title-prefix` | Title prefix for created issues | No | `"[product-manager-impersonator]"` |
| `allowed-bot-users` | Allowed bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Example: Running Multiple Personas

You can run the same workflow multiple times with different personas and title prefixes to get ideas from different perspectives:

```yaml
name: Ideas
on:
  schedule:
    - cron: "0 9 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  iterative-idea:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-product-manager-impersonator.lock.yml@v0
    with:
      idea-size: "small"
      title-prefix: "[idea]"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  sre-idea:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-product-manager-impersonator.lock.yml@v0
    with:
      persona: "a seasoned SRE and platform engineer who lives in logs, metrics, and distributed traces"
      idea-size: "small"
      title-prefix: "[observability idea]"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  security-idea:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-product-manager-impersonator.lock.yml@v0
    with:
      persona: "a seasoned threat-hunter and SOC engineer who lives in dashboards, detection rules, and XDR alert queues"
      idea-size: "medium"
      title-prefix: "[security idea]"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

## Safe Outputs

- `create-issue` — file a feature idea (max 1 per run)
