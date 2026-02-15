---
# DO NOT EDIT — this is a synced copy. Source: .github/workflows/gh-aw-fragments/safe-output-review-comment.md
safe-outputs:
  create-pull-request-review-comment:
    max: 30
---

## create-pull-request-review-comment Limitations

- **Required fields**: `path` (file path), `line` (line number), and `body` (comment text).
- **Line**: Must be within the diff — an added or context line in the patch. Lines outside the diff will fail.
- **Body**: Sanitized with the standard pipeline (mentions neutralized, HTML filtered, URLs restricted). GitHub API limit is ~65,536 characters.
- **Side**: Defaults to `RIGHT` (the new code). Use `LEFT` only when commenting on deleted lines.
- **Suggestion blocks**: Use ` ```suggestion ` fences for concrete code fixes. The suggestion must actually change the code — don't suggest identical code.
