---
safe-outputs:
  create-pull-request:
---

## create-pull-request Limitations

- **Patch files**: Max 100 files per PR. If changes span more files, split into multiple focused PRs.
- **Patch size**: Max 1,024 KB by default. Keep changes focused.
- **Title**: Max 128 characters. Sanitized.
- **Body**: No explicit mention/link limits, but bot triggers (`fixes #123`, `closes #456`) are neutralized.
- **Committed changes required**: You must have locally committed changes before creating a PR (unless `allow_empty` is configured).
- **Base branch**: Must be configured in the safe-output config. The PR targets this branch.
- **Max per run**: Typically 1 PR creation per workflow run.
- You may not submit code that touches anything in ./github/workflows. Doing so will cause your entire submission to be rejected. If you are asked to do so, propose your change in a copy of the file you place in a `github` folder (without the period) and include in your pull request that the file needs to be relocated by someone with access to update workflows.