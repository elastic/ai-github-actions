---
safe-inputs:
  ready-to-make-pr:
    description: "Run the PR readiness checklist before creating or updating a PR"
    py: |
      import os, json
      def find(*paths):
          return next((p for p in paths if os.path.isfile(p)), None)
      contributing = find('CONTRIBUTING.md', 'CONTRIBUTING.rst', 'docs/CONTRIBUTING.md', 'docs/contributing.md')
      pr_template = find('.github/pull_request_template.md', '.github/PULL_REQUEST_TEMPLATE.md', '.github/PULL_REQUEST_TEMPLATE/pull_request_template.md')
      checklist = []
      if contributing: checklist.append(f'Review the contributing guide ({contributing}) before opening or updating a PR.')
      if pr_template: checklist.append(f'Follow the PR template ({pr_template}) for title, description, and validation notes.')
      checklist.append('Confirm the requested task is fully completed and validated before creating or pushing PR changes.')
      checklist.append('Spawn a code-review sub-agent via runSubagent to self-review your changes before creating the PR. Include the full diff (git diff) in the prompt along with relevant context (what was requested, which files changed, and why). The sub-agent should look for bugs, logic errors, missed edge cases, and style issues. Fix any legitimate issues it finds before proceeding.')
      print(json.dumps({'status': 'ok', 'checklist': checklist, 'contributing_guide': contributing, 'pr_template': pr_template}))
safe-outputs:
  create-pull-request:
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
- You may not submit code that modifies files in `.github/workflows/`. Doing so will cause the submission to be rejected. If asked to modify workflow files, propose the change in a copy placed in a `github/` folder (without the leading period) and note in the PR that the file needs to be relocated by someone with workflow write access.
