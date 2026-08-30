#!/usr/bin/env bash
# extract-lockfile-prompts.sh — Extract agent prompt text from compiled .lock.yml files.
#
# Usage: ./scripts/extract-lockfile-prompts.sh [input-dir] [output-dir]
#   input-dir:  directory containing .lock.yml files (default: .github/workflows)
#   output-dir: where to write extracted .prompt.md files (default: /tmp/prompt-audit)
#
# Wrapper around the Python extractor. Keep this shell entrypoint because
# workflows call this script directly.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/extract_lockfile_prompts.py" "$@"
