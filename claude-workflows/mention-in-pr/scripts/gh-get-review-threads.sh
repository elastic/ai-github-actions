#!/usr/bin/env bash
set -euo pipefail

# Get PR review threads with comments via GitHub GraphQL API
#
# Usage:
#   gh-get-review-threads.sh [FILTER]
#
# Arguments:
#   FILTER - Optional: filter for unresolved threads from specific author
#
# Environment (set by composite action):
#   MENTION_REPO      - Repository (owner/repo format)
#   MENTION_PR_NUMBER - Pull request number
#   GITHUB_TOKEN      - GitHub API token
#
# Output:
#   JSON array of review threads with nested comments

# Parse OWNER and REPO from MENTION_REPO
REPO_FULL="${MENTION_REPO:?MENTION_REPO environment variable is required}"
OWNER="${REPO_FULL%/*}"
REPO="${REPO_FULL#*/}"
PR_NUMBER="${MENTION_PR_NUMBER:?MENTION_PR_NUMBER environment variable is required}"
FILTER="${1:-}"

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
                  }
                }
              }
            }
          }
        }
      }' -F owner="$OWNER" \
         -F repo="$REPO" \
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
                  }
                }
              }
            }
          }
        }
      }' -F owner="$OWNER" \
         -F repo="$REPO" \
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
              }
            }
          }
        }
      }' -F threadId="$thread_id"
  fi
}

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

if [ -n "$FILTER" ]; then
  echo "$THREADS" | jq --arg author "$FILTER" '
    map(select(
      .isResolved == false and
      .comments.nodes | any(.author.login == $author)
    ))'
else
  echo "$THREADS"
fi
