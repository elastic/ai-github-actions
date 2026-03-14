---
safe-outputs:
  reply-to-pull-request-review-comment:
    max: 10
    target: "${{ inputs.target-pr-number || 'triggering' }}"
---

## reply-to-pull-request-review-comment Limitations

- **Required field**: `comment_id` — the numeric REST comment ID (e.g., `2481734562`). From `get_review_comments` this is the `id` field. From `/tmp/pr-context/review_comments.json` (GraphQL) this is the `databaseId` field. Do not pass GraphQL node IDs (e.g., `IC_kwDONVGiRc6...`) — those will fail.
- **Body**: Max 65,536 characters. Keep well under this limit.
- **Purpose**: Reply directly to a specific review comment thread to explain your reasoning when you disagree with or skip feedback. Do NOT use `add_comment` for this — use this tool to keep replies in context.
- **Max per run**: 10 replies per workflow run.
