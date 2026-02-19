#!/usr/bin/env bash
# Move files from github/ to .github/ — workaround for gh-aw agents
# that can't write to dot-prefixed directories.
#
# Usage:
#   ./scripts/move-github-dotgithub.sh          # move only
#   ./scripts/move-github-dotgithub.sh --push   # move, commit, and push
set -euo pipefail

push=false
for arg in "$@"; do
  case "$arg" in
    --push) push=true ;;
    -h|--help)
      echo "Usage: $0 [--push]"
      echo "  --push  git add, commit, and push after moving files"
      exit 0
      ;;
    *) echo "Unknown flag: $arg"; exit 1 ;;
  esac
done

src="github"

if [ ! -d "$src" ]; then
  echo "No '$src' directory found — nothing to move."
  exit 0
fi

count=0
moved_files=()
while IFS= read -r -d '' file; do
  rel="${file#$src/}"
  dest=".github/$rel"
  mkdir -p "$(dirname "$dest")"
  mv "$file" "$dest"
  echo "  $src/$rel → $dest"
  moved_files+=("$dest")
  ((count++))
done < <(find "$src" -type f -print0)

# Clean up empty directories left behind
find "$src" -type d -empty -delete 2>/dev/null
rmdir "$src" 2>/dev/null || true

echo "Moved $count file(s) from $src/ to .github/"

if [ "$push" = true ] && [ "$count" -gt 0 ]; then
  git add "${moved_files[@]}"
  git add "$src"
  git commit -m "Move agent output from github/ to .github/"
  git push
  echo "Committed and pushed."
fi
