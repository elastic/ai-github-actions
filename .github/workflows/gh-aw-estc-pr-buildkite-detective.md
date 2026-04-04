---
inlined-imports: true
description: "Analyze failed Buildkite PR checks and report findings"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-add-comment-pr-hide-older.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
on:
  stale-check: false
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      additional-instructions:
        description: "Repo-specific instructions appended to the agent prompt"
        type: string
        required: false
        default: ""
      setup-commands:
        description: "Shell commands to run before the agent starts (dependency install, build, etc.)"
        type: string
        required: false
        default: ""
      allowed-bot-users:
        description: "Allowed bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      BUILDKITE_API_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
    - "buildkite-limited-access[bot]"
concurrency:
  group: ${{ github.workflow }}-estc-pr-buildkite-detective-${{ github.event.check_run.id || github.run_id }}
  cancel-in-progress: false
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, actions]
  bash: true
  web-fetch:
network:
  allowed:
    - "buildkite.com"
safe-outputs:
  activation-comments: false
  noop:
strict: false
timeout-minutes: 30
steps:
  - name: Resolve event context and fetch Buildkite data
    env:
      BUILDKITE_API_TOKEN: ${{ secrets.BUILDKITE_API_TOKEN }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_RUN_ID: ${{ github.run_id }}
      GITHUB_REPOSITORY: ${{ github.repository }}
    run: |
      python3 - << 'PYEOF'
      import json, os, re, subprocess, sys, urllib.request

      BK_TOKEN = os.environ['BUILDKITE_API_TOKEN']
      EVENT_NAME = os.environ['GITHUB_EVENT_NAME']
      LOG_TAIL = 150
      ANSI_RE = re.compile(r'\x1b(?:\[[0-9;]*[A-Za-z]|_[^\x07]*\x07|[()][AB012]|[=>])')
      BK_URL_RE = re.compile(r'https://buildkite\.com/([^/]+)/([^/]+)/builds/(\d+)')

      os.makedirs('/tmp/gh-aw/buildkite-logs', exist_ok=True)

      def bk_get(path):
          url = f'https://api.buildkite.com/v2/{path}'
          req = urllib.request.Request(url, headers={'Authorization': f'Bearer {BK_TOKEN}'})
          with urllib.request.urlopen(req) as r:
              return json.load(r)

      def slugify(name):
          return re.sub(r'\s+', '-', re.sub(r'[^\w\s-]', '', name).strip()).lower()[:60].strip('-')

      with open(os.environ['GITHUB_EVENT_PATH']) as f:
          event = json.load(f)

      if EVENT_NAME == 'status':
          commit_sha = event['commit']['sha']
          target_url = event.get('target_url', '')
      else:
          cr = event['check_run']
          commit_sha = cr['head_sha']
          target_url = cr.get('details_url', '')

      m = BK_URL_RE.search(target_url)
      if not m:
          print(f'No Buildkite build URL in target_url: {target_url}')
          sys.exit(1)

      bk_org, bk_pipeline, bk_number = m.group(1), m.group(2), m.group(3)
      build = bk_get(f'organizations/{bk_org}/pipelines/{bk_pipeline}/builds/{bk_number}')

      pr_info = build.get('pull_request') or {}
      pr_number = pr_info.get('id', '')
      branch = build.get('branch', '')

      with open('/tmp/gh-aw/buildkite-event.txt', 'w') as f:
          f.write(f'event_name: {EVENT_NAME}\n')
          f.write(f'commit_sha: {commit_sha}\n')
          f.write(f'build_url: {m.group(0)}\n')
          f.write(f'pipeline: {bk_pipeline}\n')
          f.write(f'branch: {branch}\n')
          f.write(f'pr_number: {pr_number}\n')
      print('Buildkite event context:')
      print(open('/tmp/gh-aw/buildkite-event.txt').read())

      def skip(reason):
          subprocess.run(['bash', '-c', f'echo "::notice::{reason}"'], check=False)
          print(reason)
          sys.exit(1)

      if not pr_number:
          skip('Build is not associated with a PR; skipping')

      if build['state'] not in ('failed', 'failing'):
          skip(f'Build is not finished (state: {build["state"]}); skipping')

      def collect_failed_jobs(build_data, pipeline_slug, build_url):
          """Collect failed script jobs, following trigger jobs to child builds."""
          FAIL_STATES = ('failed', 'timed_out')
          results = []

          for job in build_data.get('jobs', []):
              if job.get('state') not in FAIL_STATES:
                  continue
              if job.get('type') == 'script':
                  results.append((pipeline_slug, build_url, job))
              elif job.get('type') == 'trigger':
                  triggered = job.get('triggered_build') or {}
                  child_url = triggered.get('web_url', '')
                  cm = BK_URL_RE.search(child_url)
                  if cm:
                      child = bk_get(f'organizations/{cm.group(1)}/pipelines/{cm.group(2)}/builds/{cm.group(3)}')
                      results.extend(collect_failed_jobs(child, cm.group(2), child_url))

          return results

      failed = collect_failed_jobs(build, bk_pipeline, m.group(0))
      if not failed:
          skip(f'No failed script jobs in build (build state: {build["state"]})')

      summary = [
          f'## Build: {m.group(0)}',
          f'Pipeline: {bk_pipeline}  State: {build["state"]}',
          f'PR: #{pr_number}  Branch: {branch}',
          f'Failed jobs: {len(failed)}',
          '',
      ]

      for pipeline_slug, build_url, job in failed:
          slug = slugify(job.get('name', f'job-{job["id"]}'))
          log_file = f'/tmp/gh-aw/buildkite-logs/{pipeline_slug}-{slug}.txt'

          summary.append(f'### {job["name"]}')
          summary.append(f'Pipeline: {pipeline_slug}  Build: {build_url}')
          summary.append(f'State: {job["state"]}  Exit status: {job.get("exit_status")}')
          summary.append(f'Command: {job.get("command", "").strip()}')
          summary.append(f'Log: {log_file}')
          summary.append('')

          raw_url = job.get('raw_log_url', '')
          if raw_url:
              req = urllib.request.Request(raw_url, headers={'Authorization': f'Bearer {BK_TOKEN}'})
              with urllib.request.urlopen(req) as r:
                  lines = r.read().decode('utf-8', errors='replace').splitlines()
              with open(log_file, 'w') as f:
                  f.write('\n'.join(ANSI_RE.sub('', l) for l in lines[-LOG_TAIL:]))

      with open('/tmp/gh-aw/buildkite-failures.txt', 'w') as f:
          f.write('\n'.join(summary))
      print(f'Fetched {len(failed)} failed job(s)')
      PYEOF
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# PR Buildkite Detective

Analyze failed Buildkite CI builds for pull requests in ${{ github.repository }}. Identify root causes from build logs, trace failures to source code, and provide actionable fix recommendations via PR comments. This workflow is read-only.

## Context

- **Repository**: ${{ github.repository }}
- **Pre-fetched data**: `/tmp/gh-aw/buildkite-event.txt` (build URL, pipeline, branch, PR number, commit SHA) and `/tmp/gh-aw/buildkite-failures.txt` (failed job summary with log file paths under `/tmp/gh-aw/buildkite-logs/`)

## Constraints

- **CAN**: Read files, search code, run tests and commands, comment on PRs
- **CANNOT**: Push changes, merge PRs, or modify `.github/workflows/`

## Instructions

### Step 1: Read Pre-Fetched Data

1. Read `/tmp/gh-aw/buildkite-event.txt` for the PR number, build URL, branch, and commit SHA.
2. Read `/tmp/gh-aw/buildkite-failures.txt` for the failed job summary. If it does not exist, call `noop` with "No Buildkite failure data" and stop.
3. Read the individual log files listed in the summary (under `/tmp/gh-aw/buildkite-logs/`).
4. Call `pull_request_read` with method `get` on the PR number to get the author, diff, and recent changes.

### Step 2: Analyze

Classify each failure:

- **Code bug**: Logic error, syntax error, type mismatch, nil/null dereference
- **Test failure**: Assertion mismatch, test timeout, flaky test
- **Dependency issue**: Missing package, version conflict, lockfile drift
- **Infrastructure**: Resource exhaustion, service unavailability, timeout — recommend retry if transient
- **Configuration**: Invalid settings, missing secrets/env vars, incorrect paths

For each:

1. Identify the specific error from the logs.
2. Trace to source code using `grep` and file reading. Check recent PR changes that may have introduced the failure.
3. If the error involves an external library or tool, use `web-fetch` to check docs/changelogs.
4. Propose a concrete fix or, if inconclusive, state what additional data is needed.

**Deduplication**: Check the most recent prior detective comment on the PR. If the root cause and remediation are the same, call `noop` instead of posting a duplicate.

### Step 3: Respond

Call `add_comment` on the PR using this structure:

```markdown
### TL;DR
[1-2 sentences: what failed and the immediate action needed]

## Remediation
- [specific fix step]
- [specific validation step]

<details>
<summary>Investigation details</summary>

## Root Cause
[concise explanation with file paths and line numbers where applicable]

## Evidence
- Build: [link to Buildkite build]
- Job/step: [name]
- Key log excerpt: [snippet]

## Verification
- [tests/commands run or "not run" with reason]

## Follow-up
- [optional next steps]

</details>
```

Put the TL;DR and Remediation outside the `<details>` block so they are immediately visible. Put root cause evidence, log excerpts, tests run, and follow-up details inside the collapsed block.

${{ inputs.additional-instructions }}
