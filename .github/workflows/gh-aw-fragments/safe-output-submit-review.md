---
safe-outputs:
  submit-pull-request-review:
    max: 1
    footer: "if-body"
    target: "${{ inputs.target-pr-number || 'triggering' }}"
---

## submit-pull-request-review Limitations

- **Event**: Must be one of `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`. Defaults to `COMMENT` if omitted.
- **Body**: Max 65,000 characters. If you have cross-cutting feedback that spans multiple files or cannot be expressed as inline comments, include it here. Otherwise, leave the review body empty — your inline comments already contain the detail. A body is required when event is `REQUEST_CHANGES`. Sanitized (mentions neutralized, HTML filtered, URLs restricted). If you have also used `create-pull-request-review-comment`, you do not need to repeat the same feedback in the body. If you "Approve" and have no comments, do not provide a `body`.
- **Own PRs**: If the workflow actor is also the PR author (e.g., `github-actions[bot]` reviewing its own PR), the event is forced to `COMMENT` regardless of what you specify. `APPROVE` and `REQUEST_CHANGES` will not work.
- **Max per run**: 1 review submission per workflow run. Leave inline comments first, then submit the review as a single final action.

**Do NOT** describe what the PR does, list the files you reviewed, summarize inline comments, or restate prior review feedback. The PR author already knows what their PR does. Your inline comments already contain all the detail. The review body exists solely to communicate the approve/request-changes decision and important/critical feedback that cannot be covered in inline comments.
