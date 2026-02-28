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
      | `threads/<path>.json` | Per-file review threads — one file per changed file with existing threads, mirroring the repo path under `threads/` |
      | `comments.json` | PR discussion comments (not inline) |
      | `issue-{N}.json` | Linked issue details (one file per linked issue, if any) |
      | `agents.md` | Repository conventions from `generate_agents_md` (if written by agent) |
      | `review-instructions.md` | Review instructions, criteria, and calibration examples (if written by review-process fragment) |
      MANIFEST

      echo "PR context written to /tmp/pr-context/"
      ls -la /tmp/pr-context/
---

## PR Context

PR data is pre-fetched to `/tmp/pr-context/`. Read `/tmp/pr-context/README.md` for a manifest of all available files. Use these as your primary source for PR metadata, diffs, reviews, comments, and linked issues; fall back to API tools only when required data is unavailable.
