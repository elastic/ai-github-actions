---
safe-outputs:
  reply-to-pull-request-review-comment:
    max: 10
---

## reply-to-pull-request-review-comment Limitations

- **Required field**: `comment_id` — the ID of the review comment to reply to. This is the numeric REST comment ID from `get_review_comments`.
- **Body**: Max 65,536 characters. Keep well under this limit.
- **Purpose**: Reply directly to a specific review comment thread to explain your reasoning when you disagree with or skip feedback. Do NOT use `add_comment` for this — use this tool to keep replies in context.
- **Max per run**: 10 replies per workflow run.
