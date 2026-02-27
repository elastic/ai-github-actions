# Docs Patrol

Detect code changes that require documentation updates — both internal and published.

Two variants cover different documentation scopes: **Docs Patrol** checks internal documentation (READMEs, CONTRIBUTING, etc.) against recent code changes, while **Docs Patrol External (Elastic-specific)** focuses on published Elastic documentation on `elastic.co/docs`. Both scan recent commits for public API or behavioral changes not reflected in documentation. Most runs end with `noop`.

## Quick install

### Internal docs only

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-patrol/example.yml \
  -o .github/workflows/docs-patrol.yml
```

### Both internal and external

```bash
mkdir -p .github/workflows && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-patrol/example.yml \
  -o .github/workflows/docs-patrol.yml && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-docs-patrol-external/example.yml \
  -o .github/workflows/estc-docs-patrol-external.yml
```

---

## Docs Patrol (internal)

Scans recent commits (7-day lookback by default) for public API or behavioral changes not reflected in nearby documentation. Checks READMEs, contribution guides, and other discovered markdown files before filing.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `lookback-window` | Git lookback window for detecting recent commits | `"7 days ago"` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-issue` — file a docs patrol report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Docs Patrol
on:
  schedule:
    - cron: "0 14 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-docs-patrol.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Docs Patrol External (Elastic-specific)

Like Docs Patrol, but focuses on changes that require updates to published Elastic documentation on `elastic.co/docs`. Also flags features that need `applies_to` tag updates or documentation backports to earlier release branches.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `lookback-window` | Git lookback window for detecting recent commits | `"7 days ago"` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-issue` — file an external docs patrol report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Docs Patrol External (Elastic-specific)
on:
  schedule:
    - cron: "0 14 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-estc-docs-patrol-external.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
