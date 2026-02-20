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
      return { status: 'ok', checklist, contributing_guide: contributing, pr_template: prTemplate };
safe-outputs:
  push-to-pull-request-branch:
---

Before calling `push_to_pull_request_branch`, call `ready_to_make_pr` and apply its checklist.

## push-to-pull-request-branch Limitations

- **Patch size**: Max 1,024 KB by default. Keep changes focused — large refactors may exceed this.
- **Fork PRs**: Cannot push to fork PR branches. Check via `pull_request_read` with method `get` whether the PR head repo differs from the base repo. If it's a fork, explain that you cannot push and suggest the author apply changes themselves.
- **Committed changes required**: You must have locally committed changes before calling push. Uncommitted or staged-only changes will fail.
- **Branch**: Pushes to the PR's head branch. The workspace must have the PR branch checked out.
- You may not submit code that modifies files in `.github/workflows/`. Doing so will cause the submission to be rejected. If asked to modify workflow files, propose the change in a copy placed in a `github/` folder (without the leading period) and note in the PR that the file needs to be relocated by someone with workflow write access.

Trying to resolve merge conflicts? Do NOT use `git merge` or `git rebase`. Instead:
1. Compare the conflicting files between this PR branch and origin/main
2. Edit the files directly to incorporate the changes from main
3. Commit the changes as regular commits
4. Use push_to_pull_request_branch to push
