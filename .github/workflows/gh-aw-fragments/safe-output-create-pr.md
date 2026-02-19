---
safe-outputs:
  create-pull-request:
    draft: ${{ inputs.draft-prs != 'false' }}
---

## create-pull-request Limitations

- **Patch files**: Max 100 files per PR. If changes span more files, split into multiple focused PRs.
- **Patch size**: Max 1,024 KB by default. Keep changes focused.
- **Title**: Max 128 characters. Sanitized.
- **Body**: No explicit mention/link limits, but bot triggers (`fixes #123`, `closes #456`) are neutralized.
- **Committed changes required**: You must have locally committed changes before creating a PR (unless `allow_empty` is configured).
- **Base branch**: Must be configured in the safe-output config. The PR targets this branch.
- **Max per run**: Typically 1 PR creation per workflow run.
- You may not submit code that modifies files in `.github/workflows/`. Doing so will cause the submission to be rejected. If asked to modify workflow files, propose the change in a copy placed in a `github/` folder (without the leading period) and note in the PR that the file needs to be relocated by someone with workflow write access.