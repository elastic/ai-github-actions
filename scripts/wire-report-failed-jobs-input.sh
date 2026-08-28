#!/usr/bin/env bash
# Wire the report-failed-jobs workflow_call input to the GH_AW_REPORT_FAILED_JOBS
# env var in compiled lock files.
#
# The gh-aw compiler hard-codes GH_AW_REPORT_FAILED_JOBS: "true" in every compiled
# lock file. This script replaces that hardcoded value with an expression that reads from
# the report-failed-jobs workflow_call input so callers can opt out of failed job
# reporting.
#
# Only lock files that already define the report-failed-jobs input (i.e. those that
# were compiled from a workflow with that input in their on.workflow_call.inputs block)
# are modified. Internal-only workflows without workflow_call are skipped automatically.
#
# Usage:
#   ./scripts/wire-report-failed-jobs-input.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"

OLD='          GH_AW_REPORT_FAILED_JOBS: "true"'
NEW="          GH_AW_REPORT_FAILED_JOBS: \${{ inputs.report-failed-jobs && 'true' || 'false' }}"

count=0
for lock_file in "$WORKFLOWS_DIR"/gh-aw-*.lock.yml; do
  # Only process lock files that define the report-failed-jobs input
  if ! grep -q "report-failed-jobs:" "$lock_file" 2>/dev/null; then
    continue
  fi
  # Skip if already wired
  if ! grep -qF "$OLD" "$lock_file" 2>/dev/null; then
    continue
  fi
  # Use a temp file for portability (BSD + GNU sed)
  tmp=$(mktemp)
  while IFS= read -r line; do
    if [ "$line" = "$OLD" ]; then
      printf '%s\n' "$NEW"
    else
      printf '%s\n' "$line"
    fi
  done < "$lock_file" > "$tmp"
  mv "$tmp" "$lock_file"
  echo "  ✓ $(basename "$lock_file")"
  count=$((count + 1))
done

echo "✓ Wired report-failed-jobs in $count lock file(s)"
