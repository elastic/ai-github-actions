#!/usr/bin/env bash
# Validate that every uses: entry with an @ includes a non-empty ref.
# Example invalid line: uses: ruby/setup-ruby@ # v1.319.0
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"

if [ ! -d "$WORKFLOWS_DIR" ]; then
  echo "No .github/workflows directory found; skipping uses-ref validation."
  exit 0
fi

invalid_count=0

while IFS= read -r -d '' workflow_file; do
  while IFS= read -r match; do
    invalid_count=$((invalid_count + 1))
    echo "Invalid uses reference: ${workflow_file#$REPO_ROOT/}:$match"
  done < <(grep -nE '^[[:space:]]*uses:[[:space:]]+[^[:space:]#]+@[[:space:]]*(#.*)?$' "$workflow_file" || true)
done < <(find "$WORKFLOWS_DIR" -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) -print0)

if [ "$invalid_count" -gt 0 ]; then
  echo ""
  echo "Found $invalid_count invalid uses reference(s)."
  echo "Each uses: entry with @ must include a non-empty ref (tag, branch, or SHA)."
  exit 1
fi

echo "✓ uses references validation passed"
