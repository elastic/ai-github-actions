---
safe-inputs:
  ready-to-code-review:
    description: "Prepare code review instructions based on PR size — writes agent-review.md, parent-review.md, and subagent-*.md to /tmp/pr-context/"
    py: |
      import os, json, re

      os.makedirs('/tmp/pr-context', exist_ok=True)

      # Read PR size written by the pr-context step
      try:
          with open('/tmp/pr-context/pr-size.txt') as f:
              pr_size = f.read().strip()
          m = re.search(r', (\d+) diff', pr_size)
          diff_lines = int(m.group(1)) if m else 0
      except Exception:
          pr_size = 'unknown size'
          diff_lines = 0

      # Write one instruction file per sub-agent file ordering strategy
      for key, desc in [('az', 'A \u2192 Z (alphabetical)'), ('za', 'Z \u2192 A (reverse alphabetical)'), ('largest', 'largest diff first')]:
          lines = [
              '# PR Review Sub-Agent',
              '',
              'Review the PR as a code review sub-agent. Return findings only \u2014 do NOT leave inline comments.',
              '',
              '## Instructions',
              '',
              'Read `/tmp/pr-context/review-instructions.md` for the full review process, criteria, calibration examples, and output format.',
              '',
              '## Context',
              '',
              '- Repository conventions: `/tmp/agents.md` (skip if missing)',
              '- PR details: `/tmp/pr-context/pr.json`',
              '- All context files: `/tmp/pr-context/README.md`',
              '- Per-file diffs: `/tmp/pr-context/diffs/<filename>.diff`',
              '- Full file contents: read from the workspace (PR branch is checked out)',
              '',
              '## Your File Order',
              '',
              f'Review files in this order: `/tmp/pr-context/file_order_{key}.txt` ({desc})',
          ]
          with open(f'/tmp/pr-context/subagent-{key}.md', 'w') as f:
              f.write('\n'.join(lines) + '\n')

      # Determine review approach based on PR size
      if diff_lines < 200:
          approach_lines = [
              f'**Small PR ({pr_size}):** Review directly \u2014 no sub-agents. Review files in order from `/tmp/pr-context/file_order_az.txt`, reading each diff from `/tmp/pr-context/diffs/<filename>.diff` and the full file from the workspace.',
          ]
          size_key = 'small'
      elif diff_lines < 800:
          approach_lines = [
              f'**Medium PR ({pr_size}):** Use the **Pick Three, Keep Many** process \u2014 spawn 2 `code-review` sub-agents in parallel:',
              '',
              '- **Agent 1**: prompt it to read `/tmp/pr-context/subagent-az.md` and follow it',
              '- **Agent 2**: prompt it to read `/tmp/pr-context/subagent-za.md` and follow it',
              '',
              'Each sub-agent returns a structured findings list. They do NOT leave inline comments.',
          ]
          size_key = 'medium'
      else:
          approach_lines = [
              f'**Large PR ({pr_size}):** Use the **Pick Three, Keep Many** process \u2014 spawn 3 `code-review` sub-agents in parallel:',
              '',
              '- **Agent 1**: prompt it to read `/tmp/pr-context/subagent-az.md` and follow it',
              '- **Agent 2**: prompt it to read `/tmp/pr-context/subagent-za.md` and follow it',
              '- **Agent 3**: prompt it to read `/tmp/pr-context/subagent-largest.md` and follow it',
              '',
              'Each sub-agent returns a structured findings list. They do NOT leave inline comments.',
          ]
          size_key = 'large'

      with open('/tmp/pr-context/agent-review.md', 'w') as f:
          f.write('\n'.join(approach_lines) + '\n')

      # Write parent-agent comment format and threshold instructions
      t3 = chr(96) * 3
      t5 = chr(96) * 5
      threshold = os.environ.get('GH_AW_INPUTS_MINIMUM_SEVERITY', 'low') or 'low'
      parent_lines = [
          '# Code Review: Comment Format and Threshold',
          '',
          '## Comment Format',
          '',
          'Call **`create_pull_request_review_comment`** with:',
          '- The file path and the **exact line number from reading the file** (not estimated from the diff)',
          '- The line must be within the diff (an added or context line in the patch)',
          '',
          t5,
          '**[SEVERITY] Brief title**',
          '',
          'Description of the issue and why it matters.',
          '',
          f'{t3}suggestion',
          'corrected code here',
          t3,
          t5,
          '',
          'Only include a `suggestion` block when you can provide a concrete code fix that **actually changes** the code. If the fix requires structural changes, describe the fix in prose instead — never include a suggestion identical to the original line.',
          '',
          '## Inline Comment Threshold',
          '',
          f'The minimum severity for inline comments is `{threshold}`.',
          '',
          'Issues at or above the threshold get **inline review comments** on the specific code line. Issues below the threshold should be collected into a **collapsible section** of the review body — use a `<details>` block titled "Lower-priority observations (N)" with each item listing its severity, title, file:line, and why it matters.',
          '',
          'Severity order (highest to lowest): critical > high > medium > low > nitpick.',
          '',
          'If the threshold is `low`, only nitpick-severity issues go in the review body. If `medium`, both low and nitpick go in the body. If the value is unrecognized, treat it as `low`.',
      ]
      with open('/tmp/pr-context/parent-review.md', 'w') as f:
          f.write('\n'.join(parent_lines) + '\n')

      print(json.dumps({'status': 'ok', 'size': size_key, 'diff_lines': diff_lines, 'agent_review': '/tmp/pr-context/agent-review.md', 'parent_review': '/tmp/pr-context/parent-review.md'}))
---
