#!/bin/bash
# pr-existing-comments.sh - Fetch existing review threads on a PR
#
# Usage:
#   pr-existing-comments.sh              - Show all review threads with full details
#   pr-existing-comments.sh --summary    - Show per-file summary only (for large PRs)
#   pr-existing-comments.sh --unresolved - Show only unresolved threads
#   pr-existing-comments.sh --file <path> - Show threads for a specific file
#   pr-existing-comments.sh --full       - Show full comment text (no truncation)
#
# Output: Formatted summary of existing review threads grouped by file,
# showing thread status, comments, and whether issues were addressed.
#
# For large PRs, use --summary first to see the overview, then --file <path>
# to get full thread details when reviewing each file.
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO       - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER  - Pull request number

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"

OWNER="${REPO%/*}"
REPO_NAME="${REPO#*/}"

# Parse arguments
FILTER_UNRESOLVED=false
FILTER_FILE=""
SUMMARY_ONLY=false
FULL_TEXT=false

while [ $# -gt 0 ]; do
  case "$1" in
    --unresolved)
      FILTER_UNRESOLVED=true
      shift
      ;;
    --file)
      FILTER_FILE="$2"
      shift 2
      ;;
    --summary)
      SUMMARY_ONLY=true
      shift
      ;;
    --full)
      FULL_TEXT=true
      shift
      ;;
    *)
      echo "Usage: pr-existing-comments.sh [--summary] [--unresolved] [--file <path>] [--full]"
      exit 1
      ;;
  esac
done

fetch_review_threads_page() {
  local threads_after="$1"
  if [ -n "$threads_after" ]; then
    gh api graphql -f query='
      query($owner: String!, $repo: String!, $prNumber: Int!, $threadsAfter: String) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $prNumber) {
            reviewThreads(first: 100, after: $threadsAfter) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                isResolved
                isOutdated
                path
                line
                originalLine
                startLine
                originalStartLine
                diffSide
                comments(first: 50) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    id
                    body
                    author { login }
                    createdAt
                    originalCommit { abbreviatedOid }
                  }
                }
              }
            }
          }
        }
      }' -F owner="$OWNER" \
         -F repo="$REPO_NAME" \
         -F prNumber="$PR_NUMBER" \
         -F threadsAfter="$threads_after"
  else
    gh api graphql -f query='
      query($owner: String!, $repo: String!, $prNumber: Int!) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $prNumber) {
            reviewThreads(first: 100) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                isResolved
                isOutdated
                path
                line
                originalLine
                startLine
                originalStartLine
                diffSide
                comments(first: 50) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    id
                    body
                    author { login }
                    createdAt
                    originalCommit { abbreviatedOid }
                  }
                }
              }
            }
          }
        }
      }' -F owner="$OWNER" \
         -F repo="$REPO_NAME" \
         -F prNumber="$PR_NUMBER"
  fi
}

fetch_thread_comments_page() {
  local thread_id="$1"
  local comments_after="$2"
  if [ -n "$comments_after" ]; then
    gh api graphql -f query='
      query($threadId: ID!, $commentsAfter: String) {
        node(id: $threadId) {
          ... on PullRequestReviewThread {
            comments(first: 50, after: $commentsAfter) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                body
                author { login }
                createdAt
                originalCommit { abbreviatedOid }
              }
            }
          }
        }
      }' -F threadId="$thread_id" \
         -F commentsAfter="$comments_after"
  else
    gh api graphql -f query='
      query($threadId: ID!) {
        node(id: $threadId) {
          ... on PullRequestReviewThread {
            comments(first: 50) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                body
                author { login }
                createdAt
                originalCommit { abbreviatedOid }
              }
            }
          }
        }
      }' -F threadId="$thread_id"
  fi
}

# Fetch review threads and thread comments via GraphQL pagination
THREADS='[]'
THREADS_AFTER=""
while :; do
  PAGE_RESPONSE=$(fetch_review_threads_page "$THREADS_AFTER")
  PAGE_THREADS=$(echo "$PAGE_RESPONSE" | jq '.data.repository.pullRequest.reviewThreads.nodes // []')
  THREADS=$(jq -n --argjson existing "$THREADS" --argjson incoming "$PAGE_THREADS" '$existing + $incoming')

  HAS_NEXT_THREADS=$(echo "$PAGE_RESPONSE" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage // false')
  THREADS_AFTER=$(echo "$PAGE_RESPONSE" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor // ""')

  if [ "$HAS_NEXT_THREADS" != "true" ]; then
    break
  fi
done

THREADS=$(echo "$THREADS" | jq -c '.[]' | while read -r thread; do
  THREAD_ID=$(echo "$thread" | jq -r '.id')
  ALL_COMMENTS=$(echo "$thread" | jq '.comments.nodes // []')
  HAS_NEXT_COMMENTS=$(echo "$thread" | jq -r '.comments.pageInfo.hasNextPage // false')
  COMMENTS_AFTER=$(echo "$thread" | jq -r '.comments.pageInfo.endCursor // ""')

  while [ "$HAS_NEXT_COMMENTS" = "true" ]; do
    COMMENTS_RESPONSE=$(fetch_thread_comments_page "$THREAD_ID" "$COMMENTS_AFTER")
    COMMENT_NODES=$(echo "$COMMENTS_RESPONSE" | jq '.data.node.comments.nodes // []')
    ALL_COMMENTS=$(jq -n --argjson existing "$ALL_COMMENTS" --argjson incoming "$COMMENT_NODES" '$existing + $incoming')
    HAS_NEXT_COMMENTS=$(echo "$COMMENTS_RESPONSE" | jq -r '.data.node.comments.pageInfo.hasNextPage // false')
    COMMENTS_AFTER=$(echo "$COMMENTS_RESPONSE" | jq -r '.data.node.comments.pageInfo.endCursor // ""')
  done

  echo "$thread" | jq --argjson comments "$ALL_COMMENTS" '.comments = {nodes: $comments}'
done | jq -s '.')

if [ -z "$THREADS" ] || [ "$THREADS" = "null" ]; then
  echo "No existing review threads found."
  exit 0
fi

# Apply filters
FILTERED="$THREADS"

if [ "$FILTER_UNRESOLVED" = true ]; then
  FILTERED=$(echo "$FILTERED" | jq '[.[] | select(.isResolved == false)]')
fi

if [ -n "$FILTER_FILE" ]; then
  FILTERED=$(echo "$FILTERED" | jq --arg file "$FILTER_FILE" '[.[] | select(.path == $file)]')
fi

THREAD_COUNT=$(echo "$FILTERED" | jq 'length')

if [ "$THREAD_COUNT" -eq 0 ]; then
  if [ "$FILTER_UNRESOLVED" = true ]; then
    echo "No unresolved review threads found."
  elif [ -n "$FILTER_FILE" ]; then
    echo "No review threads found for ${FILTER_FILE}."
  else
    echo "No existing review threads found."
  fi
  exit 0
fi

# Count resolved vs unresolved
RESOLVED_COUNT=$(echo "$FILTERED" | jq '[.[] | select(.isResolved == true)] | length')
UNRESOLVED_COUNT=$(echo "$FILTERED" | jq '[.[] | select(.isResolved == false)] | length')
OUTDATED_COUNT=$(echo "$FILTERED" | jq '[.[] | select(.isOutdated == true)] | length')

echo "Existing review threads: ${THREAD_COUNT} total (${UNRESOLVED_COUNT} unresolved, ${RESOLVED_COUNT} resolved, ${OUTDATED_COUNT} outdated)"
echo ""

# Summary mode: show per-file counts only
if [ "$SUMMARY_ONLY" = true ]; then
  echo "Threads by file:"
  echo "$FILTERED" | jq -r '
    group_by(.path) | .[] |
    . as $threads |
    ($threads | length) as $total |
    ([$threads[] | select(.isResolved == false)] | length) as $unresolved |
    ([$threads[] | select(.isResolved == true)] | length) as $resolved |
    ([$threads[] | select(.isOutdated == true)] | length) as $outdated |
    ([$threads[] | select(.comments.nodes | length > 1)] | length) as $has_replies |
    "  " + $threads[0].path +
    " — " + ($total | tostring) + " threads" +
    " (" + ($unresolved | tostring) + " unresolved, " + ($resolved | tostring) + " resolved" +
    (if $outdated > 0 then ", " + ($outdated | tostring) + " outdated" else "" end) +
    ")" +
    (if $has_replies > 0 then " ⚠️ " + ($has_replies | tostring) + " with replies" else "" end)
  '
  echo ""
  echo "Use: pr-existing-comments.sh --file <path>  to see full thread details for a file"
  exit 0
fi

# Full detail mode: output threads grouped by file
# Show full conversation for threads with replies
FIRST_LIMIT=200
REPLY_LIMIT=300
if [ "$FULL_TEXT" = true ]; then
  FIRST_LIMIT=999999
  REPLY_LIMIT=999999
fi

echo "$FILTERED" | jq -r --argjson first_limit "$FIRST_LIMIT" --argjson reply_limit "$REPLY_LIMIT" '
  group_by(.path) | .[] |
  "## " + .[0].path + " (" + (length | tostring) + " threads)\n" +
  ([.[] |
    "  " +
    (if .isResolved then "✅ RESOLVED" elif .isOutdated then "⚠️  OUTDATED" else "🔴 UNRESOLVED" end) +
    " (line " + (if .line then (.line | tostring) elif .startLine then (.startLine | tostring) elif .originalLine then ("~" + (.originalLine | tostring)) elif .originalStartLine then ("~" + (.originalStartLine | tostring)) else "?" end) + ")" +
    # Show the commit the comment was originally made on
    (if .comments.nodes[0].originalCommit.abbreviatedOid then " [" + .comments.nodes[0].originalCommit.abbreviatedOid + "]" else "" end) +
    # Flag threads with replies — indicates a conversation happened
    (if (.comments.nodes | length) > 1 then " ← has replies" else "" end) +
    "\n" +
    ([.comments.nodes | to_entries[] |
      .value as $comment |
      .key as $idx |
      ($comment.body | gsub("\n"; " ")) as $flat |
      if $idx == 0 then
        "    @" + ($comment.author.login // "unknown") + ": " + $flat[0:$first_limit] +
        (if ($flat | length) > $first_limit then " [truncated]" else "" end)
      else
        "    ↳ @" + ($comment.author.login // "unknown") + ": " + $flat[0:$reply_limit] +
        (if ($flat | length) > $reply_limit then " [truncated]" else "" end)
      end
    ] | join("\n")) +
    "\n"
  ] | join("\n"))
'
