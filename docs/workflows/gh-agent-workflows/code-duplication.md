# Code Duplication

Find duplicate and misplaced functions, then consolidate them automatically.

**Code Duplication Detector** scans source files to find semantically related functions that live in different files, duplicate implementations of the same logic, and functions that belong in a different module. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) for a fully autonomous detect-and-fix loop. Most runs end with `noop`.

## Quick install

### Detector only

Install the detector alone if you want to review refactoring recommendations before acting.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-detector/example.yml \
  -o .github/workflows/code-duplication-detector.yml
```

### Chained (detector + fixer)

Install the chained example for autonomous detection and consolidation.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-detector/example-chained.yml \
  -o .github/workflows/code-duplication-detect-and-fix.yml
```

---

## Code Duplication Detector

Scans source files (by language or custom glob) to find semantically related functions in different files, duplicate implementations, and functions that belong in a different module. Files a report with specific refactoring recommendations.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `languages` | Comma-separated languages to analyze (ignored if `file-globs` is set) | `"go"` |
| `file-globs` | Comma-separated file globs to analyze (overrides `languages`) | `""` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-issue` — file a refactoring report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Code Duplication Detector
on:
  schedule:
    - cron: "0 12 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-duplication-detector.lock.yml@v0
    with:
      languages: "go,python,typescript"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
