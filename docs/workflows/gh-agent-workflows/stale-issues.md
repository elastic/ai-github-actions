# Stale Issues

Find resolved issues, label them as stale, and automatically close them after a 30-day grace period.

**Stale Issues Investigator** finds open issues that appear already resolved (merged PRs, code evidence, conversation consensus), labels them with a configurable stale label, and files a summary report. **Stale Issues Remediator** processes stale-labeled issues: it removes the label when someone objects ("not stale", "still relevant") and closes issues whose 30-day grace period has expired.

## Quick install

### Investigator only

Install the investigator alone if you want to review stale-issue reports and handle closure manually.

```bash
mkdir -p .github/workflows && curl -fsSL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues-investigator/example.yml \
  -o .github/workflows/stale-issues-investigator.yml
```

### Full loop (investigator + remediator)

Install both for a fully autonomous stale-issue lifecycle.

```bash
mkdir -p .github/workflows && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues-investigator/example.yml \
  -o .github/workflows/stale-issues-investigator.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues-remediator/example.yml \
  -o .github/workflows/stale-issues-remediator.yml
```

---

## Stale Issues Investigator (detector)

Investigates open issues for evidence of resolution (linked PRs, code evidence, conversation consensus). A prescan step fetches up to 500 open issues sorted by least recently updated, giving the agent an immediate view of the most likely stale candidates. Qualified issues are labeled and included in a summary report.

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
| `stale-label` | Label used to mark stale issues | `stale` |

### Safe outputs

- `create-issue` — file a stale issues report (max 1, auto-closes older reports)
- `add-labels` — apply the stale label to issues identified as likely resolved

### Example workflow

```yaml
name: Stale Issues Investigator
on:
  schedule:
    - cron: "0 15 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: read

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues-investigator.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

---

## Stale Issues Remediator (fixer)

Processes issues already labeled as stale. Removes the label when valid objections are posted after labeling, and closes issues whose 30-day grace period has expired with an explanatory comment. A prep step preloads stale-labeled issues, recent comments, and label timeline events into local JSON files.

### Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays (1h after investigator) |
| `workflow_dispatch` | Manual |

### Inputs

| Input | Description | Default |
| --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `stale-label` | Label used to mark stale issues | `stale` |

### Safe outputs

- `remove-labels` — remove the stale label when an objection is found
- `close-issue` — close issues that have been labeled stale for 30+ days

### Example workflow

```yaml
name: Stale Issues Remediator
on:
  schedule:
    - cron: "0 16 * * 1-5"
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  run:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-stale-issues-remediator.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```
