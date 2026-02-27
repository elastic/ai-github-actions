---
safe-outputs:
  update-pull-request:
    max: 1
---

## update-pull-request Limitations

- **Title**: Max 128 characters. Sanitized (special characters escaped).
- **Body**: Supports `replace` (overwrite), `append` (add to end), or `prepend` (add to start). Default is `replace`. Max ~65,536 characters (GitHub limit). Sanitized (mentions neutralized, HTML filtered, URLs restricted).
- **Bot triggers**: References like `fixes #123` or `closes #456` in the body are neutralized to prevent unintended issue closures.
- **Mentions**: `@mentions` in the body are neutralized (backticked).
- **Max per run**: 1 update per workflow run.
- **Draft**: Optionally convert the PR between draft and ready-for-review.
