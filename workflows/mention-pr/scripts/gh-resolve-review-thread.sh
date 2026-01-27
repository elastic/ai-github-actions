#!/usr/bin/env bash
set -euo pipefail

# Resolve a GitHub PR review thread, optionally posting a comment first
#
# Usage:
#   gh-resolve-review-thread.sh THREAD_ID [COMMENT]
#
# Arguments:
#   THREAD_ID - The GraphQL node ID of the review thread to resolve
#   COMMENT   - Optional: Comment body to post before resolving
#
# Environment (set by composite action):
#   MENTION_REPO      - Repository (owner/repo format)
#   MENTION_PR_NUMBER - Pull request number
#   GITHUB_TOKEN      - GitHub API token
#
# Behavior:
#   1. If COMMENT is provided, posts it as a reply to the thread
#   2. Resolves the thread
#   3. If all threads from the same review are resolved, minimizes the review

# Parse OWNER and REPO from MENTION_REPO
REPO_FULL="${MENTION_REPO:?MENTION_REPO environment variable is required}"
OWNER="${REPO_FULL%/*}"
REPO="${REPO_FULL#*/}"
PR_NUMBER="${MENTION_PR_NUMBER:?MENTION_PR_NUMBER environment variable is required}"
THREAD_ID="${1:?Thread ID required}"
COMMENT="${2:-}"

# Step 1: Get the review ID for this thread (so we can check other threads later)
REVIEW_DATA=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $prNumber) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            comments(first: 1) {
              nodes {
                pullRequestReview {
                  id
                  databaseId
                }
              }
            }
          }
        }
      }
    }
  }' -F owner="$OWNER" -F repo="$REPO" -F prNumber="$PR_NUMBER" --jq '.data.repository.pullRequest.reviewThreads.nodes')

# Extract the review ID for this specific thread
REVIEW_ID=$(echo "$REVIEW_DATA" | jq -r --arg threadId "$THREAD_ID" '
  map(select(.id == $threadId)) | .[0].comments.nodes[0].pullRequestReview.id
')

# Step 2: Post comment if provided
if [ -n "$COMMENT" ]; then
  echo "Posting comment to thread..." >&2
  gh api graphql -f query='
    mutation($threadId: ID!, $body: String!) {
      addPullRequestReviewThreadReply(input: {
        pullRequestReviewThreadId: $threadId,
        body: $body
      }) {
        comment {
          id
        }
      }
    }' -f threadId="$THREAD_ID" -f body="$COMMENT" --silent
fi

# Step 3: Resolve the thread
echo "Resolving thread..." >&2
RESOLVE_RESULT=$(gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread {
        id
        isResolved
      }
    }
  }' -f threadId="$THREAD_ID" --jq '.data.resolveReviewThread.thread')

echo "$RESOLVE_RESULT"

# Step 4: Check if all threads from this review are now resolved
if [ -n "$REVIEW_ID" ] && [ "$REVIEW_ID" != "null" ]; then
  echo "Checking if all threads from review are resolved..." >&2
  
  UNRESOLVED_COUNT=$(echo "$REVIEW_DATA" | jq --arg reviewId "$REVIEW_ID" --arg threadId "$THREAD_ID" '
    map(select(
      .comments.nodes[0].pullRequestReview.id == $reviewId and
      .isResolved == false and
      .id != $threadId
    )) | length
  ')
  
  if [ "$UNRESOLVED_COUNT" = "0" ]; then
    echo "All threads from this review are now resolved. Minimizing review..." >&2
    if gh api graphql -f query='
      mutation($subjectId: ID!) {
        minimizeComment(input: {
          subjectId: $subjectId,
          classifier: RESOLVED
        }) {
          minimizedComment {
            isMinimized
          }
        }
      }' -f subjectId="$REVIEW_ID" --silent; then
      echo "Review minimized successfully" >&2
    else
      echo "Warning: Failed to minimize review $REVIEW_ID" >&2
    fi
  else
    echo "Review still has $UNRESOLVED_COUNT unresolved thread(s)" >&2
  fi
fi
