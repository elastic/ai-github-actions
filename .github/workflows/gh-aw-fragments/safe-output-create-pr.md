---
safe-inputs:
  ready-to-make-pr:
    description: "Run the PR readiness checklist before creating or updating a PR"
    script: |
      const fs = require('fs');
      const find = (...paths) => paths.find(p => fs.existsSync(p)) || null;
      const contributing = find('CONTRIBUTING.md', 'CONTRIBUTING.rst', 'docs/CONTRIBUTING.md', 'docs/contributing.md');
      const prTemplate = find('.github/pull_request_template.md', '.github/PULL_REQUEST_TEMPLATE.md', '.github/PULL_REQUEST_TEMPLATE/pull_request_template.md');
      const checklist = [];
      if (contributing) checklist.push(`Review the contributing guide (${contributing}) before opening or updating a PR.`);
      if (prTemplate) checklist.push(`Follow the PR template (${prTemplate}) for title, description, and validation notes.`);
      checklist.push('Confirm the requested task is fully completed and validated before creating or pushing PR changes.');
      const result = { status: 'ok', checklist, contributing_guide: contributing, pr_template: prTemplate };
      console.log(JSON.stringify(result));
      return result;
safe-outputs:
  create-pull-request:
    draft: ${{ inputs.draft-prs }}
    github-token-for-extra-empty-commit: ${{ inputs.github-token-for-extra-empty-commit }}
---

Before calling `create_pull_request`, call `ready_to_make_pr` and apply its checklist.

## create-pull-request Limitations

- **Patch files**: Max 100 files per PR. If changes span more files, split into multiple focused PRs.
- **Patch size**: Max 1,024 KB by default. Keep changes focused.
- **Title**: Max 128 characters. Sanitized.
- **Body**: No explicit mention/link limits, but bot triggers (`fixes #123`, `closes #456`) are neutralized.
- **Committed changes required**: You must have locally committed changes before creating a PR (unless `allow_empty` is configured).
- **Base branch**: Must be configured in the safe-output config. The PR targets this branch.
- **Max per run**: Typically 1 PR creation per workflow run.
- You may not submit code that modifies files in `.github/workflows/`. Doing so will cause the submission to be rejected. If asked to modify workflow files, propose the change in a copy placed in a `github/` folder (without the leading period) and note in the PR that the file needs to be relocated by someone with workflow write access.
