# Newbie Contributor

Review documentation from a new contributor's perspective and automatically fix gaps.

**Newbie Contributor Patrol** reads all contributor-facing documentation as if it were a new contributor's first encounter with the project — following getting-started paths, checking for missing prerequisites, and flagging blocking gaps. An **Elastic-specific** variant also cross-references published Elastic documentation. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) for a fully autonomous detect-and-fix loop. Most runs end with `noop`.

## Quick install

### Patrol only (human reviews issues)

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example.yml \
  -o .github/workflows/newbie-contributor-patrol.yml
```

### Chained (patrol + fixer)

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example-chained.yml \
  -o .github/workflows/newbie-contributor-patrol-and-fix.yml
```

### Patrol + external (Elastic-specific)

```bash
mkdir -p .github/workflows && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example.yml \
  -o .github/workflows/newbie-contributor-patrol.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/estc-newbie-contributor-patrol-external/example.yml \
  -o .github/workflows/estc-newbie-contributor-patrol-external.yml
```

---

## Newbie Contributor Patrol (detector)

Reads all contributor-facing documentation (README, CONTRIBUTING, DEVELOPING, etc.) as if it were a new contributor's first encounter with the project. Follows getting-started paths, checks for missing prerequisites, and flags blocking gaps. Only files issues for high-impact problems.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly (Monday) |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-issue` — file a new contributor docs review (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Newbie Contributor Patrol
on:
  schedule:
    - cron: "0 11 * * 1"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-newbie-contributor-patrol.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Newbie Contributor Patrol External (Elastic-specific) (detector variant)

Like Newbie Contributor Patrol, but also cross-references the repo's documentation against published Elastic documentation on `elastic.co/docs`. Contradictions between the repo and published docs are treated as blocking issues.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly (Monday) |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-issue` — file an external new contributor docs review (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Newbie Contributor Patrol External (Elastic-specific)
on:
  schedule:
    - cron: "0 11 * * 1"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-estc-newbie-contributor-patrol-external.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
