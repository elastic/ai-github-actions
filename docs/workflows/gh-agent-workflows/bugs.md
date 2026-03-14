# Bug Hunting

Find reproducible bugs and automatically fix them.

**Bug Hunter** finds user-impacting bugs by reviewing recent git history, writing minimal reproduction scripts, and filing a report issue only when the bug is concretely confirmed. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) for a fully autonomous detect-and-fix loop. Most runs end with `noop`.

## Quick install

### Detector only

Install Bug Hunter alone if you want to review bug reports before acting on them.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-hunter/example.yml \
  -o .github/workflows/bug-hunter.yml
```

### Chained (detector + fixer)

Install the chained example for a fully autonomous bug-finding and fixing pipeline.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-hunter/example-chained.yml \
  -o .github/workflows/bug-hunt-and-fix.yml
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
