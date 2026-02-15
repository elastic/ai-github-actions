---
# DO NOT EDIT — this is a synced copy. Source: .github/workflows/gh-aw-fragments/safe-output-push-to-pr.md
safe-outputs:
  push-to-pull-request-branch:
---

## push-to-pull-request-branch Limitations

- **Patch size**: Max 1,024 KB by default. Keep changes focused — large refactors may exceed this.
- **Fork PRs**: Cannot push to fork PR branches. Check via `pull_request_read` with method `get` whether the PR head repo differs from the base repo. If it's a fork, explain that you cannot push and suggest the author apply changes themselves.
- **Committed changes required**: You must have locally committed changes before calling push. Uncommitted or staged-only changes will fail.
- **Branch**: Pushes to the PR's head branch. The workspace must have the PR branch checked out.
