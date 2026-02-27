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
      gh pr view "$PR_NUMBER" --json title,body,author,baseRefName,headRefName,url \
        > /tmp/pr-context/pr.json

      # Full diff
      gh pr diff "$PR_NUMBER" > /tmp/pr-context/pr.diff || true

      # Changed files list
      gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER/files" --paginate \
        > /tmp/pr-context/files.json

      # Per-file diffs
      jq -c '.[]' /tmp/pr-context/files.json | while IFS= read -r entry; do
        filename=$(echo "$entry" | jq -r '.filename')
        mkdir -p "/tmp/pr-context/diffs/$(dirname "$filename")"
        echo "$entry" | jq -r '.patch // empty' > "/tmp/pr-context/diffs/${filename}.diff"
      done

      # Existing reviews
      gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER/reviews" --paginate \
        > /tmp/pr-context/reviews.json

      # Existing review comments (inline threads)
      gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER/comments" --paginate \
        > /tmp/pr-context/review_comments.json

      # PR discussion comments
      gh api "repos/$GITHUB_REPOSITORY/issues/$PR_NUMBER/comments" --paginate \
        > /tmp/pr-context/comments.json

      # Linked issues
      grep -oiP '(?:fixes|closes|resolves)\s+#\K\d+' /tmp/pr-context/pr.json 2>/dev/null \
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
      | `pr.json` | PR metadata — title, body, author, base/head branches, URL |
      | `pr.diff` | Full unified diff of all changes |
      | `files.json` | Changed files array — each entry has `filename`, `status`, `additions`, `deletions`, `patch` |
      | `diffs/<path>.diff` | Per-file diffs — one file per changed file, mirroring the repo path under `diffs/` |
      | `reviews.json` | Prior review submissions — author, state (APPROVED/CHANGES_REQUESTED/COMMENTED), body |
      | `review_comments.json` | Inline review threads — file, line, body, author, whether resolved/outdated |
      | `comments.json` | PR discussion comments (not inline) |
      | `issue-{N}.json` | Linked issue details (one file per linked issue, if any) |
      | `agents.md` | Repository conventions from `generate_agents_md` (if written by agent) |
      | `review-instructions.md` | Review instructions, criteria, and calibration examples (if written by review-process fragment) |
      MANIFEST

      echo "PR context written to /tmp/pr-context/"
      ls -la /tmp/pr-context/
---

## PR Context

PR data is pre-fetched to `/tmp/pr-context/`. Read `/tmp/pr-context/README.md` for a manifest of all available files. Use these files instead of making API calls for PR metadata, diffs, reviews, comments, and linked issues.
