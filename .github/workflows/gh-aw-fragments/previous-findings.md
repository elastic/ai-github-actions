---
steps:
  - name: List previous findings
    env:
      GH_TOKEN: ${{ github.token }}
      TITLE_PREFIX: ${{ inputs.title-prefix }}
    run: |
      set -euo pipefail
      gh issue list \
        --repo "$GITHUB_REPOSITORY" \
        --search "in:title \"$TITLE_PREFIX\"" \
        --state all \
        --limit 100 \
        --json number,title,state \
        > /tmp/previous-findings.json || { echo "::warning::Failed to fetch previous findings — dedup will be skipped"; echo "[]" > /tmp/previous-findings.json; }
---

## Previous Findings

Before filing a new issue, check `/tmp/previous-findings.json` for issues this agent has already filed.

- Run `cat /tmp/previous-findings.json` to read the list of previously filed issue numbers and titles.
- If your finding closely matches an open or recently-closed issue in that list, call `noop` instead of filing a duplicate.
- Only file a new issue when the finding is genuinely distinct from all previous findings.
