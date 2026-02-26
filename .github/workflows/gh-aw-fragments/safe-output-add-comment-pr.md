---
safe-outputs:
  add-comment:
    max: 1
    issues: false
    pull-requests: true
    discussions: false
---

## add-comment Limitations

- **Body**: Max 65,536 characters (including any footer added by gh-aw). Keep well under this limit.
- **Mentions**: Max 10 `@` mentions per comment.
- **Links**: Max 50 URLs per comment.
- **HTML**: Only safe tags allowed (`details`, `summary`, `code`, `pre`, `blockquote`, `table`, `b`, `em`, `strong`, `h1`–`h6`, `hr`, `br`, `li`, `ol`, `ul`, `p`, `sub`, `sup`). Other tags are converted to parentheses.
- **URLs**: Only HTTPS URLs to allowed domains. Non-HTTPS and non-allowed domains are redacted.
- **Bot triggers**: References like `fixes #123` or `closes #456` are neutralized to prevent unintended issue closures.

If you exceed 10 mentions or 50 links, the comment will be rejected.
