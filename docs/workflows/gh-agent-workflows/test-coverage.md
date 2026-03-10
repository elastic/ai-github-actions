# Test Coverage

Find under-tested code and automatically add focused tests.

**Test Coverage Detector** identifies code paths with no or minimal test coverage by running coverage tools (when available) and analyzing recent changes for missing tests. **Test Improver** adds focused tests that validate real behavior and cleans up redundant tests. Most runs of either workflow end with `noop`.

## Quick install

### Detector only

Install the detector alone if you want to review test coverage reports before acting.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-coverage-detector/example.yml \
  -o .github/workflows/test-coverage-detector.yml
```

### Full loop (detector + fixer)

Install both for autonomous detection and test improvement.

```bash
mkdir -p .github/workflows && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-coverage-detector/example.yml \
  -o .github/workflows/test-coverage-detector.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-improver/example.yml \
  -o .github/workflows/test-improver.yml
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

---

## Test Improver (fixer)

Identifies code paths with no or minimal test coverage, adds focused tests that validate real behavior, and removes or consolidates clearly redundant tests. Only opens a PR for changes that would catch actual regressions — not trivial getters or incidental coverage.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekly |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-pull-request` — open a PR with test improvements

### Example workflow

```yaml
name: Test Improver
on:
  schedule:
    - cron: "0 9 * * 1"
  workflow_dispatch:

permissions:
  actions: read
  contents: write
  issues: write
  pull-requests: write

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-test-improver.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
