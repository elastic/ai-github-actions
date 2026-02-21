#!/usr/bin/env bash
# Inject the close-older-issues input expression into compiled lock files.
#
# The gh-aw compiler cannot evaluate boolean expressions in safe-outputs YAML
# fields; it only accepts literal true/false. This script post-processes lock
# files that expose a close-older-issues workflow_call input by replacing the
# hardcoded "close_older_issues":true in GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG
# with ${{ inputs.close-older-issues }}, so that GitHub Actions resolves the
# value at runtime.
#
# Usage:
#   ./scripts/inject-configurable-close.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOWS_DIR="$(cd "$SCRIPT_DIR/../.github/workflows" && pwd)"

patched=0

for lock_file in "$WORKFLOWS_DIR"/gh-aw-*.lock.yml; do
  # Only process lock files that expose a close-older-issues workflow_call input
  if ! grep -q "close-older-issues:" "$lock_file"; then
    continue
  fi

  # Replace the hardcoded boolean with the input expression.
  # The JSON is embedded in a YAML string with escaped quotes: \"close_older_issues\":true
  sed -i 's/\\"close_older_issues\\":true/\\"close_older_issues\\":${{ inputs.close-older-issues }}/g' "$lock_file"
  echo "  ✓ $(basename "$lock_file"): close_older_issues → \${{ inputs.close-older-issues }}"
  patched=$((patched + 1))
done

echo "✓ inject-configurable-close: patched $patched lock file(s)"
