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

echo "Syncing workflow files..."

# Copy trigger .yml files from gh-agent-workflows/ → .github/workflows/trigger-*
for f in gh-agent-workflows/*.yml; do
  [ -e "$f" ] || continue
  name=$(basename "$f")
  cp "$f" ".github/workflows/trigger-$name"
  echo "  ✓ gh-agent-workflows/$name → .github/workflows/trigger-$name"
done

echo "✓ Sync complete"
