#!/usr/bin/env bash
# Sync workflow files between their canonical locations and their copy locations.
#
# Canonical sources:
#   - Shims:     gh-agent-workflows/*.md
#   - Prompts:   .github/workflows/gh-aw-workflows/
#   - Fragments: .github/workflows/gh-aw-fragments/
#
# This script copies:
#   1. Shims → .github/workflows/       (compiler needs them here)
#   2. gh-aw-workflows/ → gh-agent-workflows/  (local import resolution + remote consumers)
#   3. gh-aw-fragments/ → gh-agent-workflows/  (local import resolution + remote consumers)
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

# Copy gh-aw-workflows/ and gh-aw-fragments/ → gh-agent-workflows/
rm -rf gh-agent-workflows/gh-aw-workflows gh-agent-workflows/gh-aw-fragments
mkdir -p gh-agent-workflows/gh-aw-workflows gh-agent-workflows/gh-aw-fragments

for f in .github/workflows/gh-aw-workflows/*.md; do
  name=$(basename "$f")
  copy_with_header "$f" "gh-agent-workflows/gh-aw-workflows/$name" ".github/workflows/gh-aw-workflows/$name"
done
echo "  ✓ .github/workflows/gh-aw-workflows/ → gh-agent-workflows/gh-aw-workflows/"

for f in .github/workflows/gh-aw-fragments/*.md; do
  name=$(basename "$f")
  copy_with_header "$f" "gh-agent-workflows/gh-aw-fragments/$name" ".github/workflows/gh-aw-fragments/$name"
done
echo "  ✓ .github/workflows/gh-aw-fragments/ → gh-agent-workflows/gh-aw-fragments/"

echo "✓ Sync complete"
