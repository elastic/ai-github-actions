---
# DO NOT EDIT — this is a synced copy. Source: .github/workflows/gh-aw-fragments/safe-output-create-issue.md
safe-outputs:
  create-issue:
---

## create-issue Limitations

- **Title**: Max 128 characters. Sanitized (special characters escaped).
- **Labels**: Max 10 labels per issue. Each label max 64 characters. Labels containing only `-` are rejected.
- **Assignees**: Max 5 assignees per issue.
- **Body**: No strict character limit beyond GitHub's API limit (~65,536 characters), but fields over 16,000 tokens are written to a file reference instead of inlined.
- **Bot triggers**: References like `fixes #123` or `closes #456` in the body are neutralized to prevent unintended issue closures.
- **Mentions**: `@mentions` in the body are neutralized (backticked) by default.
