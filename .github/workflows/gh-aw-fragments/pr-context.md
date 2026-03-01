---
steps:
  - name: Fetch PR context to disk
    env:
      GH_TOKEN: ${{ github.token }}
      PR_NUMBER: "${{ github.event.pull_request.number || inputs.target-pr-number || github.event.issue.number }}"
    run: |
      set -euo pipefail
      mkdir -p /tmp/pr-context

      # PR metadata
      gh pr view "$PR_NUMBER" --json title,body,author,baseRefName,headRefName,headRefOid,url \
        > /tmp/pr-context/pr.json

      # Full diff
      if ! gh pr diff "$PR_NUMBER" > /tmp/pr-context/pr.diff; then
        echo "::warning::Failed to fetch full PR diff; per-file diffs from files.json are still available."
        : > /tmp/pr-context/pr.diff
      fi

      # Changed files list (--paginate may output concatenated arrays; jq -s 'add' merges them)
      gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER/files" --paginate \
        | jq -s 'add // []' > /tmp/pr-context/files.json

      # Per-file diffs
      jq -c '.[]' /tmp/pr-context/files.json | while IFS= read -r entry; do
        filename=$(echo "$entry" | jq -r '.filename')
        mkdir -p "/tmp/pr-context/diffs/$(dirname "$filename")"
        echo "$entry" | jq -r '.patch // empty' > "/tmp/pr-context/diffs/${filename}.diff"
      done

      # File orderings for sub-agent review (3 strategies)
      jq -r '[.[] | .filename] | sort | .[]' /tmp/pr-context/files.json \
        > /tmp/pr-context/file_order_az.txt
      jq -r '[.[] | .filename] | sort | reverse | .[]' /tmp/pr-context/files.json \
        > /tmp/pr-context/file_order_za.txt
      jq -r '[.[] | {filename, size: ((.additions // 0) + (.deletions // 0))}] | sort_by(-.size) | .[].filename' /tmp/pr-context/files.json \
        > /tmp/pr-context/file_order_largest.txt

      # Determine sub-agent count based on PR size
      FILE_COUNT=$(jq 'length' /tmp/pr-context/files.json)
      if [ "$FILE_COUNT" -le 10 ]; then
        AGENT_COUNT=0
      elif [ "$FILE_COUNT" -le 20 ]; then
        AGENT_COUNT=2
      else
        AGENT_COUNT=3
      fi
      echo "$AGENT_COUNT" > /tmp/pr-context/agent_count.txt
      echo "PR size: ${FILE_COUNT} files → ${AGENT_COUNT} sub-agents"

      # Write review strategy with precise instructions for the agent
      echo "# Review Strategy" > /tmp/pr-context/review-strategy.md
      echo "" >> /tmp/pr-context/review-strategy.md
      echo "**PR size:** ${FILE_COUNT} files | **Sub-agents:** ${AGENT_COUNT}" >> /tmp/pr-context/review-strategy.md
      echo "" >> /tmp/pr-context/review-strategy.md

      if [ "$AGENT_COUNT" -eq 0 ]; then
        cat >> /tmp/pr-context/review-strategy.md << 'STRATEGY_DIRECT'
      ## Direct Review (no sub-agents)

      This PR is small enough to review directly. Do NOT spawn sub-agents.

      Review the diff file by file using the ordering in `/tmp/pr-context/file_order_az.txt`. For each changed file:

      1. Read the diff from `/tmp/pr-context/diffs/<filename>.diff`
      2. Read the full file from the workspace for context
      3. Check existing threads in `/tmp/pr-context/threads/<filename>.json` (if it exists)
      4. Identify issues matching the Code Review Reference criteria
      5. Verify each issue: construct a concrete failure scenario, challenge the finding, check for existing threads

      Proceed to the Verify and Comment step with your findings.
      STRATEGY_DIRECT
      elif [ "$AGENT_COUNT" -eq 2 ]; then
        cat >> /tmp/pr-context/review-strategy.md << 'STRATEGY_TWO'
      ## Sub-agent Review (2 agents)

      Spawn exactly 2 `code-review` sub-agents in parallel:

      - **Agent 1**: file ordering from `/tmp/pr-context/file_order_az.txt` (A→Z)
      - **Agent 2**: file ordering from `/tmp/pr-context/file_order_za.txt` (Z→A)

      Each sub-agent prompt must include:
      - Instruction to read `/tmp/pr-context/review-instructions.md` for the review process, criteria, and calibration examples
      - Instruction to read `/tmp/pr-context/README.md` for a manifest of all available context files
      - The review intensity and minimum severity settings from the workflow
      - The path to that sub-agent's file ordering — tell it to read the file for its ordered list (per-file diffs are at `/tmp/pr-context/diffs/<filename>.diff`)
      - Instruction to read changed files from the workspace (the PR branch is checked out)

      Each sub-agent returns a structured findings list. They do NOT leave inline comments.

      After both sub-agents complete, merge and deduplicate findings per the Pick Three, Keep Many process before proceeding to the Verify and Comment step.
      STRATEGY_TWO
      else
        cat >> /tmp/pr-context/review-strategy.md << 'STRATEGY_THREE'
      ## Sub-agent Review (3 agents)

      Spawn exactly 3 `code-review` sub-agents in parallel:

      - **Agent 1**: file ordering from `/tmp/pr-context/file_order_az.txt` (A→Z)
      - **Agent 2**: file ordering from `/tmp/pr-context/file_order_za.txt` (Z→A)
      - **Agent 3**: file ordering from `/tmp/pr-context/file_order_largest.txt` (largest diff first)

      Each sub-agent prompt must include:
      - Instruction to read `/tmp/pr-context/review-instructions.md` for the review process, criteria, and calibration examples
      - Instruction to read `/tmp/pr-context/README.md` for a manifest of all available context files
      - The review intensity and minimum severity settings from the workflow
      - The path to that sub-agent's file ordering — tell it to read the file for its ordered list (per-file diffs are at `/tmp/pr-context/diffs/<filename>.diff`)
      - Instruction to read changed files from the workspace (the PR branch is checked out)

      Each sub-agent returns a structured findings list. They do NOT leave inline comments.

      After all 3 sub-agents complete, merge and deduplicate findings per the Pick Three, Keep Many process before proceeding to the Verify and Comment step.
      STRATEGY_THREE
      fi

      # Existing reviews
      gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER/reviews" --paginate \
        | jq -s 'add // []' > /tmp/pr-context/reviews.json

      # Review threads with resolution status (GraphQL — REST lacks isResolved/isOutdated)
      gh api graphql --paginate -f query='
        query($owner: String!, $repo: String!, $number: Int!, $endCursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $number) {
              reviewThreads(first: 100, after: $endCursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  id
                  isResolved
                  isOutdated
                  isCollapsed
                  path
                  line
                  startLine
                  comments(first: 100) {
                    nodes {
                      id
                      databaseId
                      body
                      author { login }
                      createdAt
                    }
                  }
                }
              }
            }
          }
        }
      ' -F owner="${GITHUB_REPOSITORY%/*}" -F repo="${GITHUB_REPOSITORY#*/}" -F "number=$PR_NUMBER" \
        --jq '.data.repository.pullRequest.reviewThreads.nodes' \
        | jq -s 'add // []' > /tmp/pr-context/review_comments.json

      # Filtered review thread views (pre-computed so agents don't need to parse review_comments.json)
      jq '[.[] | select(.isResolved == false)]' /tmp/pr-context/review_comments.json \
        > /tmp/pr-context/unresolved_threads.json
      jq '[.[] | select(.isResolved == true)]' /tmp/pr-context/review_comments.json \
        > /tmp/pr-context/resolved_threads.json
      jq '[.[] | select(.isOutdated == true)]' /tmp/pr-context/review_comments.json \
        > /tmp/pr-context/outdated_threads.json

      # Per-file review threads (mirrors diffs/ structure)
      jq -c '.[]' /tmp/pr-context/review_comments.json | while IFS= read -r thread; do
        filepath=$(echo "$thread" | jq -r '.path // empty')
        [ -z "$filepath" ] && continue
        mkdir -p "/tmp/pr-context/threads/$(dirname "$filepath")"
        echo "$thread" >> "/tmp/pr-context/threads/${filepath}.jsonl"
      done
      # Convert per-file JSONL to proper JSON arrays
      mkdir -p /tmp/pr-context/threads
      find /tmp/pr-context/threads -name '*.jsonl' 2>/dev/null | while IFS= read -r jsonl; do
        jq -s '.' "$jsonl" > "${jsonl%.jsonl}.json"
        rm "$jsonl"
      done

      # PR discussion comments
      gh api "repos/$GITHUB_REPOSITORY/issues/$PR_NUMBER/comments" --paginate \
        | jq -s 'add // []' > /tmp/pr-context/comments.json

      # Linked issues
      jq -r '.body // ""' /tmp/pr-context/pr.json 2>/dev/null \
        | grep -oiE '(fixes|closes|resolves)\s+#[0-9]+' \
        | grep -oE '[0-9]+$' \
        | sort -u \
        | while read -r issue; do
            gh api "repos/$GITHUB_REPOSITORY/issues/$issue" > "/tmp/pr-context/issue-${issue}.json" || true
          done || true

      # Write manifest
      cat > /tmp/pr-context/README.md << 'MANIFEST'
      # PR Context

      Pre-fetched PR data. All files are in `/tmp/pr-context/`.

      | File | Description |
      | --- | --- |
      | `pr.json` | PR metadata — title, body, author, base/head branches, head commit SHA (`headRefOid`), URL |
      | `pr.diff` | Full unified diff of all changes |
      | `files.json` | Changed files array — each entry has `filename`, `status`, `additions`, `deletions`, `patch` |
      | `diffs/<path>.diff` | Per-file diffs — one file per changed file, mirroring the repo path under `diffs/` |
      | `file_order_az.txt` | Changed files sorted alphabetically (A→Z), one filename per line |
      | `file_order_za.txt` | Changed files sorted reverse-alphabetically (Z→A), one filename per line |
      | `file_order_largest.txt` | Changed files sorted by diff size descending (largest first), one filename per line |
      | `reviews.json` | Prior review submissions — author, state (APPROVED/CHANGES_REQUESTED/COMMENTED), body |
      | `review_comments.json` | All review threads (GraphQL) — each thread has `id` (node ID for resolving), `isResolved`, `isOutdated`, `path`, `line`, and nested `comments` with `id`, `databaseId` (numeric REST ID for replies), body/author |
      | `unresolved_threads.json` | Unresolved review threads — subset of `review_comments.json` where `isResolved` is false |
      | `resolved_threads.json` | Resolved review threads — subset of `review_comments.json` where `isResolved` is true |
      | `outdated_threads.json` | Outdated review threads — subset of `review_comments.json` where `isOutdated` is true (code changed since comment) |
      | `threads/<path>.json` | Per-file review threads — one file per changed file with existing threads, mirroring the repo path under `threads/` |
      | `comments.json` | PR discussion comments (not inline) |
      | `issue-{N}.json` | Linked issue details (one file per linked issue, if any) |
      | `agent_count.txt` | Pre-computed sub-agent count: `0` (≤10 files, direct review), `2` (11–20 files), or `3` (>20 files) |
      | `review-strategy.md` | Pre-computed review strategy with precise instructions for the agent based on PR size |
      | `agents.md` | Repository conventions from `generate_agents_md` (if written by agent) |
      | `review-instructions.md` | Review instructions, criteria, and calibration examples (if written by review-process fragment) |
      MANIFEST

      echo "PR context written to /tmp/pr-context/"
      ls -la /tmp/pr-context/
---

## PR Context

PR data is pre-fetched to `/tmp/pr-context/`. Read `/tmp/pr-context/README.md` for a manifest of all available files. Use these as your primary source for PR metadata, diffs, reviews, comments, and linked issues; fall back to API tools only when required data is unavailable. **Never mention these file paths or on-disk data sources in your responses** — they are internal implementation details invisible to users.
