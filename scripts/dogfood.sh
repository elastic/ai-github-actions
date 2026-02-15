#!/usr/bin/env bash
# Copy shim workflows into .github/workflows/ for local compilation.
#
# The gh-aw compiler processes .md files in .github/workflows/. Shims are
# authored in gh-agent-workflows/ and this script copies them into place.
# Prompts (gh-aw-workflows/) and fragments (gh-aw-fragments/) already live
# in .github/workflows/ as real files — no copying needed.
#
# Usage:
#   ./scripts/dogfood.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Copy a file, injecting a "DO NOT EDIT" comment after the opening --- line.
# Usage: copy_with_header <source> <dest> <canonical-path>
copy_with_header() {
  local src="$1" dest="$2" canonical="$3"
  {
    echo "---"
    echo "# DO NOT EDIT — this is a synced copy. Source: $canonical"
    tail -n +2 "$src"
  } > "$dest"
}

echo "Syncing workflow files..."

# Copy shims from gh-agent-workflows/ → .github/workflows/
for f in gh-agent-workflows/*.md; do
  name=$(basename "$f")
  case "$name" in README.md|DEVELOPING.md|AGENTS.md) continue ;; esac
  copy_with_header "$f" ".github/workflows/$name" "gh-agent-workflows/$name"
  echo "  ✓ gh-agent-workflows/$name → .github/workflows/$name"
done

echo "✓ Sync complete"
