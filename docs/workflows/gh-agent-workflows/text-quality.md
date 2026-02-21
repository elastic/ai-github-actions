# Text Quality

Find text issues and automatically fix them.

**Text Auditor** scans user-facing text sources — CLI output, error messages, documentation, and help text — for typos, grammatical errors, unclear messages, and inconsistent terminology. **Text Beautifier** picks up those reports and opens a PR with concrete fixes. Most runs of either workflow end with `noop`.

## Quick install

### Auditor only (human reviews issues)

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-auditor/example.yml \
  -o .github/workflows/text-auditor.yml
```

### Full loop (auditor + beautifier)

```bash
mkdir -p .github/workflows && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-auditor/example.yml \
  -o .github/workflows/text-auditor.yml && \
curl -sL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/text-beautifier/example.yml \
  -o .github/workflows/text-beautifier.yml
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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-text-auditor.lock.yml@e1d1b3475a1318f42c9f46c597f9b0eb0972bd74 # v0.2.5
    with:
      # edit-typos: low
      # edit-grammar: low
      # edit-clarity: low
      # edit-terminology: low
      # edit-misleading-text: low
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Text Beautifier (fixer)

Picks up open issues filed by the Text Auditor (labeled `text-auditor` or with `[text-auditor]` in the title), applies the suggested text fixes, and opens a PR. Only acts on concrete, unambiguous fixes — skips anything requiring design decisions.

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

- `create-pull-request` — open a PR with text fixes (max 1)

### Example workflow

```yaml
name: Text Beautifier
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
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-text-beautifier.lock.yml@e1d1b3475a1318f42c9f46c597f9b0eb0972bd74 # v0.2.5
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
