#!/usr/bin/env bash
# Move files from github/ to .github/ — workaround for gh-aw agents
# that can't write to dot-prefixed directories.
set -euo pipefail

src="github"

if [ ! -d "$src" ]; then
  echo "No '$src' directory found — nothing to move."
  exit 0
fi

count=0
while IFS= read -r -d '' file; do
  rel="${file#$src/}"
  dest=".github/$rel"
  mkdir -p "$(dirname "$dest")"
  mv "$file" "$dest"
  echo "  $src/$rel → $dest"
  ((count++))
done < <(find "$src" -type f -print0)

# Clean up empty directories left behind
find "$src" -type d -empty -delete 2>/dev/null
rmdir "$src" 2>/dev/null || true

echo "Moved $count file(s) from $src/ to .github/"
