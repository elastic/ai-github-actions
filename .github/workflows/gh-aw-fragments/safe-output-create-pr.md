---
safe-outputs:
  create-pull-request:
    patch-format: bundle
    draft: ${{ inputs.draft-prs }}
    github-token-for-extra-empty-commit: ${{ secrets.EXTRA_COMMIT_GITHUB_TOKEN }}
---

Before calling `create_pull_request`, call `ready_to_make_pr` and apply its checklist.

## create-pull-request Limitations

- **Patch files**: Max 100 files per PR. If changes span more files, split into multiple focused PRs.
- **Patch size**: Max ~10 MB (10,240 KB). Keep changes focused.
- **Title**: Max 128 characters. Sanitized.
- **Body**: No explicit mention/link limits, but bot triggers (`fixes #123`, `closes #456`) are neutralized.
- **Committed changes required**: You must have locally committed changes before creating a PR.
- **Base branch**: The PR targets the repository's default branch.
- **Max per run**: Typically 1 PR creation per workflow run.
