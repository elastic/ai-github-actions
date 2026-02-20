#!/usr/bin/env bash
# Prepare .github/workflows/ for local compilation.
#
# The gh-aw compiler processes .md files in .github/workflows/. This script
# copies trigger .yml files from gh-agent-workflows/ into .github/workflows/.
#
# Workflow .md files and fragments (gh-aw-fragments/) live directly in
# .github/workflows/ (canonical location).
#
# Usage:
#   ./scripts/dogfood.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Workflows that are not dogfooded in this repository.
EXCLUDED_WORKFLOWS=(
  "flaky-test-triage"
  "issue-triage-pr"
)

echo "Syncing workflow files..."

# Copy trigger example.yml files from gh-agent-workflows/*/ → .github/workflows/trigger-*
# Rewrite remote uses: references to local paths for dogfooding.
for f in gh-agent-workflows/*/example.yml; do
  [ -e "$f" ] || continue
  dir=$(basename "$(dirname "$f")")
  # Skip excluded workflows.
  skip=false
  for excluded in "${EXCLUDED_WORKFLOWS[@]}"; do
    [[ "$dir" == "$excluded" ]] && skip=true && break
  done
  if [[ "$skip" == "true" ]]; then
    echo "  ✗ gh-agent-workflows/$dir/example.yml (excluded)"
    continue
  fi
  sed 's|uses: elastic/ai-github-actions/\(.*\)@v0|uses: ./\1|' "$f" \
    > ".github/workflows/trigger-$dir.yml"
  echo "  ✓ gh-agent-workflows/$dir/example.yml → .github/workflows/trigger-$dir.yml"
done

echo "✓ Sync complete"
