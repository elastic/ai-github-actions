---
safe-inputs:
  ready-to-push-to-pr:
    description: "Run the PR readiness checklist before pushing to a PR"
    py: |
      import os, json, subprocess
      def find(*paths):
          return next((p for p in paths if os.path.isfile(p)), None)
      def run(cmd):
          try:
              return subprocess.run(cmd, capture_output=True, text=True, timeout=60)
          except subprocess.TimeoutExpired:
              return subprocess.CompletedProcess(cmd, 1, stdout='', stderr='diff timed out')

      # Guard: detect history rewrites (rebase/reset/cherry-pick)
      pr_head_sha = ''
      pr_json_path = '/tmp/pr-context/pr.json'
      if os.path.isfile(pr_json_path):
          with open(pr_json_path) as f:
              pr_data = json.load(f)
          pr_head_sha = pr_data.get('headRefOid', '')
          if pr_head_sha:
              # Check 1: PR head must be an ancestor of HEAD (no rebase/reset)
              anc = run(['git', 'merge-base', '--is-ancestor', pr_head_sha, 'HEAD'])
              if anc.returncode != 0:
                  print(json.dumps({'status': 'error', 'error': f'History rewrite detected: the original PR head ({pr_head_sha[:12]}) is not an ancestor of HEAD. This means git rebase, reset, or cherry-pick rewrote history. push_to_pull_request_branch will fail. Fix: run `git reset --hard {pr_head_sha}` to restore the PR branch to its original head, then re-apply your changes as direct file edits and commit as regular commits.'}))
                  raise SystemExit(0)

      contributing = find('CONTRIBUTING.md', 'CONTRIBUTING.rst', 'docs/CONTRIBUTING.md', 'docs/contributing.md')
      pr_template = find('.github/pull_request_template.md', '.github/PULL_REQUEST_TEMPLATE.md', '.github/PULL_REQUEST_TEMPLATE/pull_request_template.md')
      agents_md = find('AGENTS.md', 'agents.md', '.github/agents.md', '.github/AGENTS.md')
      # Generate diff of local changes for self-review.
      # Prefer anchoring to original PR head when available so base->PR merge
      # commits do not flood the self-review with upstream-only changes.
      diff_text = ''
      diff_cmds = []
      if pr_head_sha:
          diff_cmds.append(['git', 'diff', pr_head_sha])
      diff_cmds.extend([
          ['git', 'diff', '--merge-base', '@{upstream}'],
          ['git', 'diff', '@{upstream}'],
          ['git', 'diff', 'HEAD'],
      ])
      for diff_cmd in diff_cmds:
          result = run(diff_cmd)
          if result.stdout.strip():
              diff_text = result.stdout.strip()
              break
      stat_text = ''
      stat_cmds = []
      if pr_head_sha:
          stat_cmds.append(['git', 'diff', '--stat', pr_head_sha])
      stat_cmds.extend([
          ['git', 'diff', '--stat', '--merge-base', '@{upstream}'],
          ['git', 'diff', '--stat', '@{upstream}'],
          ['git', 'diff', '--stat', 'HEAD'],
      ])
      for stat_cmd in stat_cmds:
          result = run(stat_cmd)
          if result.stdout.strip():
              stat_text = result.stdout.strip()
              break
      # Capture commit messages so the sub-agent knows what changed and why
      commits_text = ''
      log_cmds = []
      if pr_head_sha:
          log_cmds.append(['git', 'log', '--format=### %s%n%n%b', f'{pr_head_sha}..HEAD'])
      log_cmds.extend([
          ['git', 'log', '--format=### %s%n%n%b', '@{upstream}..HEAD'],
          ['git', 'log', '--format=### %s%n%n%b', '-10'],
      ])
      for log_cmd in log_cmds:
          result = run(log_cmd)
          if result.stdout.strip():
              commits_text = result.stdout.strip()
              break
      os.makedirs('/tmp/self-review', exist_ok=True)
      with open('/tmp/self-review/diff.patch', 'w') as f:
          f.write(diff_text)
      with open('/tmp/self-review/stat.txt', 'w') as f:
          f.write(stat_text)
      with open('/tmp/self-review/commits.txt', 'w') as f:
          f.write(commits_text)
      # Copy task context if available (PR metadata from the pr-context step)
      has_task = False
      if os.path.isfile('/tmp/pr-context/pr.json'):
          import shutil
          shutil.copy('/tmp/pr-context/pr.json', '/tmp/self-review/task.json')
          has_task = True
      # Write manifest so the sub-agent has structured context without
      # relying on the main agent to manually pass it in the prompt
      manifest_lines = [
          '# Self-Review Context',
          '',
          'You are reviewing unpushed changes before they are submitted to a PR.',
          '',
          '## Available files',
          '',
          'All files are in `/tmp/self-review/`:',
          '',
          f'- `diff.patch` : Full unified diff of all changes ({len(diff_text.splitlines())} lines)',
          '- `stat.txt` : File-level change summary',
          '- `commits.txt` : Commit messages describing what was changed and why',
          '- `notes.md` : Author notes on what was done, why, and key decisions made',
      ]
      if has_task:
          manifest_lines.append('- `task.json` : Original PR context (title, body, author, branches)')
      step = 1
      manifest_lines += ['', '## How to review', '']
      manifest_lines.append(f'{step}. Read `notes.md` to understand what the author did, why, and what decisions they made.')
      step += 1
      manifest_lines.append(f'{step}. Read `commits.txt` for the commit-level view of what changed.')
      step += 1
      if has_task:
          manifest_lines.append(f'{step}. Read `task.json` to understand the original task or issue being addressed.')
          step += 1
      manifest_lines.append(f'{step}. Read `stat.txt` for a high-level view of which files changed.')
      step += 1
      manifest_lines.append(f'{step}. Read `diff.patch` and the relevant source files from the workspace (the branch is checked out).')
      step += 1
      if agents_md:
          manifest_lines.append(f'{step}. Read `{agents_md}` in the workspace for repository coding conventions.')
      manifest_lines += [
          '',
          '## Focus areas',
          '',
          'Look for bugs, logic errors, missed edge cases, and style issues.',
          'Focus on what the author might have MISSED rather than re-deriving their reasoning.',
          'Do not run tests, linters, or type checkers in this self-review step; the parent agent is responsible for validation and has already run the required checks.',
          '',
          '## What NOT to flag',
          '',
          '- Pre-existing issues not introduced by these changes',
          '- Style preferences handled by linters or formatters',
          '- Theoretical performance concerns without evidence of real-world impact',
      ]
      with open('/tmp/self-review/README.md', 'w') as f:
          f.write('\n'.join(manifest_lines) + '\n')
      diff_line_count = len(diff_text.splitlines())
      checklist = []
      if contributing: checklist.append(f'Review the contributing guide ({contributing}) before opening or updating a PR.')
      if pr_template: checklist.append(f'Follow the PR template ({pr_template}) for title, description, and validation notes.')
      checklist.append('Confirm the requested task is fully completed and validated before creating or pushing PR changes.')
      if diff_line_count > 0:
          checklist.append(f'A diff of your unpushed changes ({diff_line_count} lines) and supporting context have been saved to `/tmp/self-review/`. Before spawning the sub-agent, write `/tmp/self-review/notes.md` with: what you changed and why, which files matter most and what they do, edge cases you already handled, and what test coverage exists. Then spawn a `code-review` sub-agent via `runSubagent` and tell it to start by reading `/tmp/self-review/README.md`. If the sub-agent finds legitimate issues, fix them, commit, and call `ready_to_push_to_pr` again.')
      print(json.dumps({'status': 'ok', 'checklist': checklist, 'contributing_guide': contributing, 'pr_template': pr_template, 'diff_line_count': diff_line_count}))
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

1. Compare with the base branch (from `/tmp/pr-context/pr.json` field `baseRefName`) and update your local base branch refs as needed.
2. Run a merge from base into the PR branch, resolve conflicts, and commit the merge result.
3. Do **not** use `git rebase` (or other history-rewrite flows like `reset --hard` + cherry-pick).
4. Call `ready_to_push_to_pr` (which catches rewritten history) and then `push_to_pull_request_branch` to push.
