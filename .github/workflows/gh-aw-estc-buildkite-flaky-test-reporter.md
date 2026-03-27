---
inlined-imports: true
description: "Collect flaky tests from Buildkite Test Engine and file per-test GitHub issues or update existing ones"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/safe-output-add-comment-issue.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
on:
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
      buildkite-organization-slug:
        description: "Buildkite organization slug (defaults to the GitHub organization name)"
        type: string
        required: false
        default: ""
      buildkite-test-suite-slugs:
        description: "Space-separated list of Buildkite test suite slugs to scan (defaults to all suites in the organization)"
        type: string
        required: false
        default: ""
      min-occurrences:
        description: "Minimum number of flaky occurrences required to report a test"
        type: number
        required: false
        default: 2
      issue-label:
        description: "Label to apply to created issues (must exist in the repository)"
        type: string
        required: false
        default: "flaky-test"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
      BUILDKITE_API_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: ${{ github.workflow }}-estc-buildkite-flaky-test-reporter
  cancel-in-progress: true
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
  create-issue:
    max: 20
    expires: 30d
  add-comment:
    max: 20
    issues: true
    pull-requests: false
timeout-minutes: 60
steps:
  - name: Fetch flaky tests from Buildkite Test Engine
    env:
      BUILDKITE_API_TOKEN: ${{ secrets.BUILDKITE_API_TOKEN }}
      GITHUB_REPOSITORY: ${{ github.repository }}
      BK_ORG_SLUG: ${{ inputs.buildkite-organization-slug }}
      BK_SUITE_SLUGS: ${{ inputs.buildkite-test-suite-slugs }}
      MIN_OCCURRENCES: ${{ inputs.min-occurrences }}
    run: |
      python3 - << 'PYEOF'
      import json, os, sys, urllib.request, urllib.parse

      BK_TOKEN = os.environ['BUILDKITE_API_TOKEN']
      GITHUB_REPOSITORY = os.environ['GITHUB_REPOSITORY']
      MIN_OCCURRENCES = int(os.environ.get('MIN_OCCURRENCES', '2'))

      # Infer Buildkite org slug from GitHub org if not provided
      bk_org = os.environ.get('BK_ORG_SLUG', '').strip()
      if not bk_org:
          bk_org = GITHUB_REPOSITORY.split('/')[0]

      suite_slugs_env = os.environ.get('BK_SUITE_SLUGS', '').strip()
      requested_suites = [s for s in suite_slugs_env.split() if s] if suite_slugs_env else []

      os.makedirs('/tmp/gh-aw/buildkite-flaky', exist_ok=True)

      def bk_get(path, params=None):
          url = f'https://api.buildkite.com/v2/{path}'
          if params:
              url += '?' + urllib.parse.urlencode(params)
          req = urllib.request.Request(url, headers={'Authorization': f'Bearer {BK_TOKEN}'})
          try:
              with urllib.request.urlopen(req) as r:
                  return json.load(r)
          except urllib.error.HTTPError as e:
              print(f'HTTP {e.code} for {url}: {e.read().decode("utf-8", errors="replace")}')
              return None

      def bk_get_all(path, params=None):
          """Fetch all pages of a Buildkite API endpoint."""
          results = []
          page = 1
          while True:
              p = dict(params or {})
              p['page'] = page
              p['per_page'] = 100
              data = bk_get(path, p)
              if not data:
                  break
              if isinstance(data, list):
                  if not data:
                      break
                  results.extend(data)
                  if len(data) < 100:
                      break
                  page += 1
              else:
                  results.append(data)
                  break
          return results

      # Fetch test suites
      print(f'Fetching test suites for organization: {bk_org}')
      suites = bk_get_all(f'analytics/organizations/{bk_org}/suites')
      if suites is None:
          print(f'ERROR: Could not fetch test suites for organization "{bk_org}". Check BUILDKITE_API_TOKEN and organization slug.')
          sys.exit(1)

      if requested_suites:
          suites = [s for s in suites if s.get('slug') in requested_suites]
          print(f'Filtered to {len(suites)} requested suite(s): {requested_suites}')
      else:
          print(f'Found {len(suites)} suite(s)')

      all_flaky = []

      for suite in suites:
          suite_slug = suite.get('slug', '')
          suite_name = suite.get('name', suite_slug)
          print(f'Fetching flaky tests for suite: {suite_name} ({suite_slug})')

          tests = bk_get_all(
              f'analytics/organizations/{bk_org}/suites/{suite_slug}/tests',
              {'filter[flaky]': 'true', 'order_by': 'flaky_occurrences', 'order_direction': 'desc'}
          )
          if not tests:
              print(f'  No flaky tests found in suite {suite_slug}')
              continue

          for test in tests:
              occurrences = test.get('flaky_occurrences', 0) or 0
              if occurrences < MIN_OCCURRENCES:
                  continue
              all_flaky.append({
                  'suite_slug': suite_slug,
                  'suite_name': suite_name,
                  'id': test.get('id', ''),
                  'scope': test.get('scope', ''),
                  'name': test.get('name', ''),
                  'location': test.get('location', ''),
                  'file_name': test.get('file_name', ''),
                  'reliability': test.get('reliability', None),
                  'flaky_occurrences': occurrences,
                  'buildkite_url': f'https://buildkite.com/{bk_org}/test-engine/suites/{suite_slug}/tests/{test.get("id", "")}',
              })

      print(f'Total flaky tests (min {MIN_OCCURRENCES} occurrences): {len(all_flaky)}')

      summary = {
          'organization': bk_org,
          'github_repository': GITHUB_REPOSITORY,
          'min_occurrences': MIN_OCCURRENCES,
          'suite_count': len(suites),
          'flaky_test_count': len(all_flaky),
          'flaky_tests': all_flaky,
      }
      out = '/tmp/gh-aw/buildkite-flaky/flaky-tests.json'
      with open(out, 'w') as f:
          json.dump(summary, f, indent=2)
      print(f'Results written to {out}')
      PYEOF
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: eval "$SETUP_COMMANDS"
---

# Buildkite Flaky Test Reporter

Report flaky tests from the Buildkite Test Engine for **${{ github.repository }}** into GitHub issues. One issue per unique flaky test; add a follow-up comment when a previously reported test is still flaky.

## Context

- **Repository**: ${{ github.repository }}
- **Pre-fetched data**: `/tmp/gh-aw/buildkite-flaky/flaky-tests.json`
  - Contains: `organization`, `github_repository`, `min_occurrences`, `suite_count`, `flaky_test_count`, `flaky_tests[]`
  - Each entry has: `suite_slug`, `suite_name`, `id`, `scope`, `name`, `location`, `file_name`, `reliability`, `flaky_occurrences`, `buildkite_url`
- **Issue label**: `${{ inputs.issue-label }}`

## Constraints

- **CAN**: Read files, search issues, create issues, add comments on issues
- **CANNOT**: Push changes, open PRs, modify `.github/workflows/`

## Instructions

### Step 1: Read Pre-Fetched Data

1. Read `/tmp/gh-aw/buildkite-flaky/flaky-tests.json`.
2. If `flaky_test_count` is 0, call `noop` with "No flaky tests found meeting the minimum occurrence threshold" and stop.

### Step 2: Check for Existing Issues

For each flaky test in the data:

1. Search open issues in this repository using the test name and scope as keywords plus the label `${{ inputs.issue-label }}` (if it exists in the repo).
2. Classify the test as:
   - **NEW** — no open issue found for this test
   - **KNOWN** — an open issue already tracks this test

Check whether the label `${{ inputs.issue-label }}` exists in the repository before using it. If it does not exist, omit it from the `create-issue` call.

### Step 3: Handle New Flaky Tests

For each **NEW** flaky test, call `create_issue` with:

**Title**: `Flaky test: <scope> :: <name>` (truncated to 128 chars if needed; omit `<scope> :: ` when scope is empty)

**Body**:

```markdown
## Flaky Test Report

**Test Suite**: <suite_name>
**Test**: <scope> :: <name> (omit scope if empty)
**Location**: <file_name>:<location> (omit if empty)
**Reliability**: <reliability as percentage, e.g. "87.3%"> (omit if null)
**Flaky occurrences**: <flaky_occurrences>

### Buildkite Test Engine

[View in Buildkite Test Engine](<buildkite_url>)

### Suggested Actions

- [ ] Investigate root cause of flakiness
- [ ] Fix or quarantine the test
- [ ] Verify stability after fix
```

**Labels**: `["${{ inputs.issue-label }}"]` — only if the label exists in the repository.

### Step 4: Update Existing Issues

For each **KNOWN** flaky test (open issue already exists), call `add_comment` on the existing issue with:

```markdown
## Still Flaky

This test is still reported as flaky in the Buildkite Test Engine.

**Flaky occurrences**: <flaky_occurrences>
**Reliability**: <reliability as percentage> (omit if null)

[View in Buildkite Test Engine](<buildkite_url>)
```

### Step 5: Noop if Nothing to Do

If all flaky tests are already tracked by open issues and no comments are needed (i.e., a comment was already added recently), call `noop` with a summary like "All <N> flaky tests are already tracked by open issues".

${{ inputs.additional-instructions }}
