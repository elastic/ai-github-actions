---
safe-outputs:
  create-pull-request-review-comment:
    max: ${{ inputs.create-pull-request-review-comment-max }}
---

## create-pull-request-review-comment

- **Required fields**: `path` (file path), `line` (line number), and `body` (comment text).
- **Line**: Must be a numbered line in the per-file diff (`/tmp/pr-context/diffs/<filename>.diff`). Only lines with a number prefix are commentable. Lines outside the diff will fail with a GitHub API error.
- **Body**: Sanitized with the standard pipeline (mentions neutralized, HTML filtered, URLs restricted). GitHub API limit is ~65,536 characters.
- **Side**: Defaults to `RIGHT` (the new code). Use `LEFT` only when commenting on deleted lines.
- **Suggestion blocks**: Use ` ```suggestion ` fences for concrete code fixes. The suggestion must actually change the code — don't suggest identical code. Only include a `suggestion` block when you can provide a concrete code fix that **actually changes** the code.

Only flag issues you are confident are real problems — false positives erode trust. Once you have flagged an issue, you cannot unflag it.