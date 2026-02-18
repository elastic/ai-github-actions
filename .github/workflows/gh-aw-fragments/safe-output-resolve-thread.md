---
safe-outputs:
  resolve-pull-request-review-thread:
    max: 10
---

## resolve-pull-request-review-thread Limitations

- **Required field**: `thread_id` — the GraphQL node ID of the review thread (e.g., `PRRT_kwDO...`). This is the `id` field from `get_review_comments`, not the numeric REST comment ID.
- **Only resolve what you've addressed**: Do not resolve threads you skipped, disagreed with, or didn't fix. Only resolve threads where your changes directly address the feedback.
- **Max per run**: 10 thread resolutions per workflow run.
