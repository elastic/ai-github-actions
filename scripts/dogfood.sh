#!/usr/bin/env bash
# Prepare .github/workflows/ for local compilation.
#
# The gh-aw compiler processes .md files in .github/workflows/. This script:
#   1. Copies shim .md files from gh-agent-workflows/ into .github/workflows/
#   2. Ensures the gh-aw-fragments symlink is a real symlink (core.symlinks=false workaround)
#
# Prompts (gh-aw-workflows/) live in .github/workflows/ as real files.
# Fragments (gh-aw-fragments/) live in gh-agent-workflows/ and are symlinked
# into .github/workflows/.
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

# Ensure a path is a real symlink (core.symlinks=false checks out symlinks as text files).
# Usage: ensure_symlink <path> <target>
ensure_symlink() {
  local path="$1" target="$2"
  if [ -L "$path" ]; then
    return
  fi
  rm -rf "$path"
  ln -s "$target" "$path"
  echo "  ✓ $path → $target"
}

echo "Syncing workflow files..."

# Copy shims from gh-agent-workflows/ → .github/workflows/
for f in gh-agent-workflows/*.md; do
  name=$(basename "$f")
  case "$name" in README.md|DEVELOPING.md|AGENTS.md) continue ;; esac
  copy_with_header "$f" ".github/workflows/$name" "gh-agent-workflows/$name"
  echo "  ✓ gh-agent-workflows/$name → .github/workflows/$name"
done

# Ensure symlinks are real (git with core.symlinks=false checks them out as text files)
ensure_symlink .github/workflows/gh-aw-fragments ../../gh-agent-workflows/gh-aw-fragments

echo "✓ Sync complete"
