---
# DO NOT EDIT — this is a synced copy. Source: .github/workflows/gh-aw-fragments/safe-output-add-comment.md
safe-outputs:
  add-comment:
---

## add-comment Limitations

- **Body**: Max 65,536 characters (including any footer added by gh-aw). Keep well under this limit.
- **Mentions**: Max 10 `@username` mentions per comment. Excess mentions are neutralized (backticked).
- **Links**: Max 50 URLs per comment. Excess links are redacted.
- **HTML**: Only safe tags allowed (`details`, `summary`, `code`, `pre`, `blockquote`, `table`, `b`, `em`, `strong`, `h1`–`h6`, `hr`, `br`, `li`, `ol`, `ul`, `p`, `sub`, `sup`). Other tags are converted to parentheses.
- **URLs**: Only HTTPS URLs to allowed domains. Non-HTTPS and non-allowed domains are redacted.
- **Bot triggers**: References like `fixes #123` or `closes #456` are neutralized to prevent unintended issue closures.
