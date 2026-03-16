# Text Quality

Find text issues and automatically fix them.

**Text Auditor** scans user-facing text sources — CLI output, error messages, documentation, and help text — for typos, grammatical errors, unclear messages, and inconsistent terminology. You can [chain it to Create PR from Issue](../detector-fixer-chaining.md) for a fully autonomous detect-and-fix loop. Most runs end with `noop`.

## Quick install

### Auditor only (human reviews issues)

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-auditor/example.yml \
  -o .github/workflows/text-auditor.yml
```

---

## Text Auditor (detector)

Scans user-facing text sources for typos, grammatical errors, unclear error messages, and inconsistent terminology. Files a single issue with concrete, low-effort fixes.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `edit-typos` | How aggressively to flag typos and misspellings (`high`/`low`/`none`) | `low` |
| `edit-grammar` | How aggressively to flag grammar problems (`high`/`low`/`none`) | `low` |
| `edit-clarity` | How aggressively to flag unclear text (`high`/`low`/`none`) | `low` |
| `edit-terminology` | How aggressively to flag inconsistent terminology (`high`/`low`/`none`) | `low` |
| `edit-misleading-text` | How aggressively to flag text that conflicts with behavior (`high`/`low`/`none`) | `low` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |

### Safe outputs

- `create-issue` — file a text improvement report (max 1, auto-closes older reports)

### Example workflow

```yaml
name: Text Auditor
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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-text-auditor.lock.yml@v0
    # with:
      # edit-typos: low
      # edit-grammar: low
      # edit-clarity: low
      # edit-terminology: low
      # edit-misleading-text: low
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
