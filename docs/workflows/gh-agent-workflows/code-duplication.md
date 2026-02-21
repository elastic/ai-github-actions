# Code Duplication

Find duplicate and misplaced functions, then consolidate them automatically.

**Code Duplication Detector** scans source files to find semantically related functions that live in different files, duplicate implementations of the same logic, and functions that belong in a different module. **Code Duplication Fixer** picks up those reports and opens a PR with behavior-preserving refactors. Most runs of either workflow end with `noop`.

## Quick install

### Detector only

Install the detector alone if you want to review refactoring recommendations before acting.

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-detector/example.yml \
  -o .github/workflows/code-duplication-detector.yml
```

### Full loop (detector + fixer)

Install both for autonomous detection and consolidation.

```bash
mkdir -p .github/workflows && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-detector/example.yml \
  -o .github/workflows/code-duplication-detector.yml && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-fixer/example.yml \
  -o .github/workflows/code-duplication-fixer.yml
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

View the workflow file: [`gh-aw-code-duplication-detector.md`](https://github.com/elastic/ai-github-actions/blob/main/.github/workflows/gh-aw-code-duplication-detector.md)

---

## Code Duplication Fixer

Picks up open issues filed by the detector (labeled `refactor` or with `[refactor]` in the title), selects one well-scoped finding, refactors the duplicate or misplaced code, runs tests, and opens a PR. Only acts on safe, behavior-preserving refactors.

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

- `create-pull-request` — open a PR with the refactor (max 1)

### Example workflow

```yaml
name: Code Duplication Fixer
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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-code-duplication-fixer.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

View the workflow file: [`gh-aw-code-duplication-fixer.md`](https://github.com/elastic/ai-github-actions/blob/main/.github/workflows/gh-aw-code-duplication-fixer.md)
