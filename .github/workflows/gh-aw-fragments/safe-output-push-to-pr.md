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

      # Guard: detect history rewrites and merge commits
      pr_json_path = '/tmp/pr-context/pr.json'
      if os.path.isfile(pr_json_path):
          with open(pr_json_path) as f:
              pr_data = json.load(f)
          pr_head_sha = pr_data.get('headRefOid', '')
          if pr_head_sha:
              # Check 1: PR head must be an ancestor of HEAD (no rebase/reset)
              anc = run(['git', 'merge-base', '--is-ancestor', pr_head_sha, 'HEAD'])
              if anc.returncode != 0:
                  print(json.dumps({'status': 'error', 'error': f'History rewrite detected: the original PR head ({pr_head_sha[:12]}) is not an ancestor of HEAD. This means git rebase, reset, or cherry-pick rewrote history. push_to_pull_request_branch will fail. Fix: reset to the PR head with `git checkout {pr_head_sha}`, re-apply your changes as direct file edits, and commit as regular commits.'}))
                  raise SystemExit(0)
              # Check 2: no merge commits (multiple parents) since PR head
              log = run(['git', 'rev-list', '--min-parents=2', f'{pr_head_sha}..HEAD'])
              merge_shas = log.stdout.strip()
              if merge_shas:
                  print(json.dumps({'status': 'error', 'error': f'Merge commit(s) detected: {merge_shas.splitlines()[0][:12]}... push_to_pull_request_branch uses git format-patch which breaks on merge commits. Fix: reset to the PR head with `git checkout {pr_head_sha}`, re-apply your changes as direct file edits (no git merge/rebase/commit-tree with multiple -p flags), and commit as regular single-parent commits.'}))
                  raise SystemExit(0)

      contributing = find('CONTRIBUTING.md', 'CONTRIBUTING.rst', 'docs/CONTRIBUTING.md', 'docs/contributing.md')
      pr_template = find('.github/pull_request_template.md', '.github/PULL_REQUEST_TEMPLATE.md', '.github/PULL_REQUEST_TEMPLATE/pull_request_template.md')
      # Generate diff of all local changes vs upstream for self-review
      # Try --merge-base (committed+staged+unstaged vs upstream), fall back to
      # @{upstream} 2-dot (committed only), then HEAD (uncommitted only)
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
  push-to-pull-request-branch:
    github-token-for-extra-empty-commit: ${{ secrets.EXTRA_COMMIT_GITHUB_TOKEN }}
---

Before calling `push_to_pull_request_branch`, call `ready_to_make_pr` and apply its checklist.

## push-to-pull-request-branch Limitations

- **Patch size**: Max ~10 MB (10,240 KB). Keep changes focused — very large refactors may exceed this.
- **Fork PRs**: Cannot push to fork PR branches. Check via `pull_request_read` with method `get` whether the PR head repo differs from the base repo. If it's a fork, explain that you cannot push and suggest the author apply changes themselves.
- **Committed changes required**: You must have locally committed changes before calling push. Uncommitted or staged-only changes will fail.
- **Branch**: Pushes to the PR's head branch. The workspace must have the PR branch checked out.
- You may not submit code that modifies files in `.github/workflows/`. Doing so will cause the submission to be rejected. If asked to modify workflow files, propose the change in a copy placed in a `github/` folder (without the leading period) and note in the PR that the file needs to be relocated by someone with workflow write access.

Trying to resolve merge conflicts? Do NOT create merge commits (commits with multiple parents) — `push_to_pull_request_branch` uses `git format-patch` which breaks on merge commits. This means: no `git merge`, no `git rebase`, no `git commit-tree` with multiple `-p` flags. Instead:
1. Use `git merge-tree` or `git diff` to compare the conflicting files between this PR branch and the PR base branch (read from `/tmp/pr-context/pr.json`)
2. Edit the files directly to incorporate the changes from the base branch
3. Commit the changes as regular (single-parent) commits
4. Use push_to_pull_request_branch to push
