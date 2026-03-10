# Bug Hunting

Find reproducible bugs and automatically fix them.

**Bug Hunter** finds user-impacting bugs by reviewing recent git history, writing minimal reproduction scripts, and filing a report issue only when the bug is concretely confirmed. **Bug Exterminator** picks up those reports, reproduces the bug locally, and opens a PR with a minimal fix. Most runs of either workflow end with `noop`.

## Quick install

### Detector only

Install Bug Hunter alone if you want to review bug reports before acting on them.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-hunter/example.yml \
  -o .github/workflows/bug-hunter.yml
```

### Full loop (detector + fixer)

Install both for a fully autonomous bug-finding and fixing pipeline.

```bash
mkdir -p .github/workflows && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-hunter/example.yml \
  -o .github/workflows/bug-hunter.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-exterminator/example.yml \
  -o .github/workflows/bug-exterminator.yml
```

---

## Bug Hunter (detector)

Reviews 28 days of git history for user-facing changes that could introduce bugs. For each candidate, writes a new minimal reproduction script and runs it — filing a report only when the bug is concretely confirmed.

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

- `create-issue` — file a bug report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Bug Hunter
on:
  schedule:
    - cron: "0 11 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Bug Exterminator (fixer)

Searches for open issues labeled `bug-hunter` or titled `[bug-hunter]`. For each candidate, attempts to reproduce the bug locally — if reproduction succeeds and a minimal fix is safe to apply, it opens a PR.

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

- `create-pull-request` — open a PR with the fix

### Example workflow

```yaml
name: Bug Exterminator
on:
  schedule:
    - cron: "0 13 * * 1-5"
  workflow_dispatch:

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-exterminator.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
