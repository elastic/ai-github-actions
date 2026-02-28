---
safe-inputs:
  ready-to-make-pr:
    description: "Run the PR readiness checklist before creating or updating a PR"
    py: |
      import os, json, subprocess
      def find(*paths):
          return next((p for p in paths if os.path.isfile(p)), None)
      def run(cmd):
          try:
              return subprocess.run(cmd, capture_output=True, text=True, timeout=60)
          except subprocess.TimeoutExpired:
              return subprocess.CompletedProcess(cmd, 1, stdout='', stderr='diff timed out')

      # Guard: detect merge commits
      # Find the fork point with the upstream branch to scope the check
      upstream_sha = ''
      for ref in ['@{upstream}', 'origin/HEAD', 'origin/main']:
          r = run(['git', 'merge-base', 'HEAD', ref])
          if r.returncode == 0 and r.stdout.strip():
              upstream_sha = r.stdout.strip()
              break
      if not upstream_sha:
          print(json.dumps({'status': 'error', 'error': 'Unable to determine upstream fork point for merge-commit validation. Fix: ensure remotes are fetched and a tracking branch is set (e.g., `git branch --set-upstream-to origin/<default-branch>`), then rerun ready_to_make_pr.'}))
          raise SystemExit(0)
      log = run(['git', 'rev-list', '--min-parents=2', f'{upstream_sha}..HEAD'])
      if log.returncode != 0:
          print(json.dumps({'status': 'error', 'error': f'Failed to check for merge commits (git rev-list exited {log.returncode}): {log.stderr.strip()}. Cannot verify commit history is safe for PR creation.'}))
          raise SystemExit(0)
      merge_shas = log.stdout.strip()
      if merge_shas:
          print(json.dumps({'status': 'error', 'error': f'Merge commit(s) detected: {merge_shas.splitlines()[0][:12]}... create_pull_request uses git format-patch which breaks on merge commits. Fix: re-apply your changes as direct file edits (no git merge/rebase/commit-tree with multiple -p flags) and commit as regular single-parent commits.'}))
          raise SystemExit(0)

      contributing = find('CONTRIBUTING.md', 'CONTRIBUTING.rst', 'docs/CONTRIBUTING.md', 'docs/contributing.md')
      pr_template = find('.github/pull_request_template.md', '.github/PULL_REQUEST_TEMPLATE.md', '.github/PULL_REQUEST_TEMPLATE/pull_request_template.md')
      # Generate diff of all local changes vs upstream for self-review
      # Try --merge-base (vs common ancestor), fall back to
      # @{upstream} 2-dot (vs upstream tip), then HEAD (uncommitted only)
      diff_text = ''
      for diff_cmd in [
          ['git', 'diff', '--merge-base', '@{upstream}'],
          ['git', 'diff', '@{upstream}'],
          ['git', 'diff', 'HEAD'],
      ]:
          result = run(diff_cmd)
          if result.stdout.strip():
              diff_text = result.stdout.strip()
              break
      stat_text = ''
      for stat_cmd in [
          ['git', 'diff', '--stat', '--merge-base', '@{upstream}'],
          ['git', 'diff', '--stat', '@{upstream}'],
          ['git', 'diff', '--stat', 'HEAD'],
      ]:
          result = run(stat_cmd)
          if result.stdout.strip():
              stat_text = result.stdout.strip()
              break
      os.makedirs('/tmp/self-review', exist_ok=True)
      with open('/tmp/self-review/diff.patch', 'w') as f:
          f.write(diff_text)
      with open('/tmp/self-review/stat.txt', 'w') as f:
          f.write(stat_text)
      diff_line_count = len(diff_text.splitlines())
      checklist = []
      if contributing: checklist.append(f'Review the contributing guide ({contributing}) before opening or updating a PR.')
      if pr_template: checklist.append(f'Follow the PR template ({pr_template}) for title, description, and validation notes.')
      checklist.append('Confirm the requested task is fully completed and validated before creating or pushing PR changes.')
      if diff_line_count > 0:
          checklist.append(f'A diff of your unpushed changes ({diff_line_count} lines) has been saved to `/tmp/self-review/diff.patch` (full diff) and `/tmp/self-review/stat.txt` (summary). Spawn a `code-review` sub-agent via `runSubagent` to review the diff against the codebase. Tell it to read `/tmp/self-review/diff.patch` and the relevant source files, and look for bugs, logic errors, missed edge cases, and style issues. If the sub-agent finds legitimate issues, fix them, commit, and call `ready_to_make_pr` again to regenerate the diff before proceeding.')
      print(json.dumps({'status': 'ok', 'checklist': checklist, 'contributing_guide': contributing, 'pr_template': pr_template, 'diff_line_count': diff_line_count}))
safe-outputs:
  create-pull-request:
    draft: ${{ inputs.draft-prs }}
    github-token-for-extra-empty-commit: ${{ secrets.EXTRA_COMMIT_GITHUB_TOKEN }}
---

Before calling `create_pull_request`, call `ready_to_make_pr` and apply its checklist. When the checklist asks you to spawn a `code-review` sub-agent, always pass `model: "${{ inputs.model }}"` to `runSubagent`.

## create-pull-request Limitations

- **Patch files**: Max 100 files per PR. If changes span more files, split into multiple focused PRs.
- **Patch size**: Max ~10 MB (10,240 KB). Keep changes focused.
- **Title**: Max 128 characters. Sanitized.
- **Body**: No explicit mention/link limits, but bot triggers (`fixes #123`, `closes #456`) are neutralized.
- **Committed changes required**: You must have locally committed changes before creating a PR.
- **Base branch**: The PR targets the repository's default branch.
- **Max per run**: Typically 1 PR creation per workflow run.
- You may not submit code that modifies files in `.github/workflows/`. Doing so will cause the submission to be rejected. If asked to modify workflow files, propose the change in a copy placed in a `github/` folder (without the leading period) and note in the PR that the file needs to be relocated by someone with workflow write access.
