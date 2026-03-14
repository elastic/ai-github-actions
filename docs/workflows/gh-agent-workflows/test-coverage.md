# Test Coverage

Find under-tested code and automatically add focused tests.

**Test Coverage Detector** identifies code paths with no or minimal test coverage by running coverage tools (when available) and analyzing recent changes for missing tests. Chain it to [Create PR from Issue](../detector-fixer-chaining.md) for a fully autonomous detect-and-fix loop. Most runs end with `noop`.

## Quick install

### Detector only

Install the detector alone if you want to review test coverage reports before acting.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-coverage-detector/example.yml \
  -o .github/workflows/test-coverage-detector.yml
```

### Chained (detector + fixer)

Install the chained example for autonomous detection and test improvement.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-coverage-detector/example-chained.yml \
  -o .github/workflows/test-coverage-detect-and-fix.yml
```

---

## Test Coverage Detector

Identifies code paths with no or minimal test coverage by running coverage tools (when available) and analyzing recent changes for missing tests. Files a report with specific, actionable recommendations for each gap — including the user scenario and suggested test approach.

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

- `create-issue` — file a test coverage report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Test Coverage Detector
on:
  schedule:
    - cron: "0 10 * * 1-5"
  workflow_dispatch:

permissions:
  actions: read
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-test-coverage-detector.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
