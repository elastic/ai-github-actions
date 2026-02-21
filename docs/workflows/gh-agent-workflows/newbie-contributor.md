# Newbie Contributor

Review documentation from a new contributor's perspective and automatically fix gaps.

**Newbie Contributor Patrol** reads all contributor-facing documentation as if it were a new contributor's first encounter with the project — following getting-started paths, checking for missing prerequisites, and flagging blocking gaps. An **External** variant also cross-references published Elastic documentation. **Newbie Contributor Fixer** picks up patrol issues and opens PRs with documentation improvements. Most runs end with `noop`.

## Quick install

### Patrol only (human reviews issues)

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example.yml \
  -o .github/workflows/newbie-contributor-patrol.yml
```

### Full loop (patrol + fixer)

```bash
mkdir -p .github/workflows && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example.yml \
  -o .github/workflows/newbie-contributor-patrol.yml && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-fixer/example.yml \
  -o .github/workflows/newbie-contributor-fixer.yml
```

### All three (patrol + external + fixer)

```bash
mkdir -p .github/workflows && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol/example.yml \
  -o .github/workflows/newbie-contributor-patrol.yml && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-patrol-external/example.yml \
  -o .github/workflows/newbie-contributor-patrol-external.yml && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/newbie-contributor-fixer/example.yml \
  -o .github/workflows/newbie-contributor-fixer.yml
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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-newbie-contributor-patrol.lock.yml@e1d1b3475a1318f42c9f46c597f9b0eb0972bd74 # v0.2.5
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Newbie Contributor Patrol External (detector variant)

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
name: Newbie Contributor Patrol External
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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-newbie-contributor-patrol-external.lock.yml@e1d1b3475a1318f42c9f46c597f9b0eb0972bd74 # v0.2.5
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Newbie Contributor Fixer

Picks up open issues filed by the patrol (labeled `newbie-contributor` or with `[newbie-contributor]` in the title), applies the suggested documentation improvements, and opens a PR. Focuses on filling gaps in the contributor onboarding path — missing prerequisites, broken commands, undocumented requirements.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-pull-request` — open a PR with documentation fixes (max 1)

### Example workflow

```yaml
name: Newbie Contributor Fixer
on:
  schedule:
    - cron: "0 14 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: read
  pull-requests: write

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-newbie-contributor-fixer.lock.yml@e1d1b3475a1318f42c9f46c597f9b0eb0972bd74 # v0.2.5
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
