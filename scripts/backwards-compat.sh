#!/usr/bin/env bash
# Generate backwards-compatibility workflow copies for renamed lock files.
#
# Downstream consumers referencing old workflow names via workflow_call will
# continue to work until they migrate to the new names. Each generated file
# includes a deprecation header comment.
#
# Usage:
#   ./scripts/backwards-compat.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"

# Parallel arrays: old name → new name
OLD_NAMES=(
  "gh-aw-breaking-change-detect.lock.yml"
  "gh-aw-deep-research.lock.yml"
  "gh-aw-docs-drift.lock.yml"
  "gh-aw-estc-downstream-health.lock.yml"
  "gh-aw-pr-ci-detective.lock.yml"
  "gh-aw-stale-issues.lock.yml"
  "gh-aw-test-improvement.lock.yml"
)
NEW_NAMES=(
  "gh-aw-breaking-change-detector.lock.yml"
  "gh-aw-internal-gemini-cli-web-search.lock.yml"
  "gh-aw-docs-patrol.lock.yml"
  "internal-downstream-health.lock.yml"
  "gh-aw-pr-actions-detective.lock.yml"
  "gh-aw-stale-issues-investigator.lock.yml"
  "gh-aw-test-improver.lock.yml"
)

for i in "${!OLD_NAMES[@]}"; do
  old_name="${OLD_NAMES[$i]}"
  new_name="${NEW_NAMES[$i]}"
  src="$WORKFLOWS_DIR/$new_name"
  dst="$WORKFLOWS_DIR/$old_name"

  if [ ! -f "$src" ]; then
    echo "  ✗ $new_name not found — skipping $old_name"
    continue
  fi

  # Remove existing symlink or file
  rm -f "$dst"

  {
    echo "# ⚠️  DEPRECATED — This workflow has been renamed."
    echo "# This file is a backwards-compatibility copy and will be removed in a future release."
    echo "# Please update your workflow reference to use the new name:"
    echo "#   $old_name → $new_name"
    echo "#"
    cat "$src"
  } > "$dst"

  echo "  ✓ $old_name → $new_name (backwards-compat copy)"
done

echo "✓ Backwards-compat sync complete"
