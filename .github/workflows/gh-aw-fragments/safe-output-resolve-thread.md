---
safe-outputs:
  resolve-pull-request-review-thread:
    max: ${{ inputs.resolve-pull-request-review-thread-max }}
---

## resolve-pull-request-review-thread Limitations

- **Required field**: `thread_id` — the GraphQL node ID of the review thread (e.g., `PRRT_kwDO...`). This is the `id` field from `get_review_comments`, not the numeric REST comment ID.
- **Only resolve what you've addressed**: Do not resolve threads you skipped, disagreed with, or didn't fix. Only resolve threads where your changes directly address the feedback.
- **Max per run**: ${{ inputs.resolve-pull-request-review-thread-max }} thread resolutions per workflow run.
