#!/usr/bin/env bash
set -euo pipefail

find_first() {
  for candidate in "$@"; do
    if [[ -f "$candidate" ]]; then
      printf '%s' "$candidate"
      return
    fi
  done
}

contributing="$(find_first CONTRIBUTING.md CONTRIBUTING.rst docs/CONTRIBUTING.md docs/contributing.md || true)"
pr_template="$(find_first .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE.md .github/PULL_REQUEST_TEMPLATE/pull_request_template.md || true)"

python - "$contributing" "$pr_template" <<'PY'
import json
import sys

contributing = sys.argv[1] or None
pr_template = sys.argv[2] or None

print(json.dumps({
    "status": "ok",
    "checklist": [
        "Review the repository's contributing guide before opening or updating a PR.",
        "Follow the PR template for title, description, and validation notes.",
        "Confirm the requested task is fully completed and validated before creating or pushing PR changes."
    ],
    "contributing_guide": contributing,
    "pr_template": pr_template
}))
PY
