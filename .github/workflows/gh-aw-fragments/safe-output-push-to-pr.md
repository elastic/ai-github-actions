---
safe-outputs:
  push-to-pull-request-branch:
    target: "triggering"
    github-token-for-extra-empty-commit: ${{ secrets.EXTRA_COMMIT_GITHUB_TOKEN }}
    protected-files: allowed
---

Before calling `push_to_pull_request_branch`, call `ready_to_push_to_pr` and apply its checklist.

## push-to-pull-request-branch Limitations

- **Patch size**: Max ~10 MB (10,240 KB). Keep changes focused — very large refactors may exceed this.
- **Fork PRs**: Cannot push to fork PR branches. Check via `pull_request_read` with method `get` whether the PR head repo differs from the base repo. If it's a fork, explain that you cannot push and suggest the author apply changes themselves.
- **Committed changes required**: You must have locally committed changes before calling push. Uncommitted or staged-only changes will fail.
- **Branch**: Pushes to the PR's head branch. The workspace must have the PR branch checked out.

Trying to resolve merge conflicts? Use merge-based conflict resolution. Rebase remains disallowed:

1. Compare with the base branch (from `/tmp/gh-aw/agent/pr-context/pr.json` field `baseRefName`) and update your local base branch refs as needed.
2. Run a merge from base into the PR branch, resolve conflicts, and commit the merge result.
3. Do **not** use `git rebase` (or other history-rewrite flows like `reset --hard` + cherry-pick).
4. Call `ready_to_push_to_pr` (which catches rewritten history) and then `push_to_pull_request_branch` to push.
