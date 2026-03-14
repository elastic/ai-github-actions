# Code Complexity

Find overly complex code and file a simplification report.

**Code Complexity Detector** scans source files for overly complex code — deep nesting, redundant conditionals, style outliers, and inline logic that reimplements existing helpers. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) for a fully autonomous detect-and-fix loop. Most runs end with `noop`.

## Quick install

### Detector only

Install the detector alone if you want to review complexity reports before acting.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-complexity-detector/example.yml \
  -o .github/workflows/code-complexity-detector.yml
```

### Chained (detector + fixer)

Install the chained example for autonomous detection and simplification.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-complexity-detector/example-chained.yml \
  -o .github/workflows/code-complexity-detect-and-fix.yml
```

---

## Code Complexity Detector

Scans source files (by language or custom glob) for overly complex code — deep nesting, redundant conditionals, style outliers, and inline logic that reimplements existing helpers. Files a report with specific simplification recommendations.

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

- `create-issue` — file a complexity report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Code Complexity Detector
on:
  schedule:
    - cron: "0 13 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-complexity-detector.lock.yml@v0
    with:
      languages: "go,python,typescript"
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
