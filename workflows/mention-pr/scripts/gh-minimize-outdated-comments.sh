#!/usr/bin/env bash
set -euo pipefail

# Minimize all but the most recent comment/review from each author on a PR
#
# Usage:
#   gh-minimize-outdated-comments.sh
#
# Environment (set by composite action):
#   MENTION_REPO      - Repository (owner/repo format)
#   MENTION_PR_NUMBER - Pull request number
#   GITHUB_TOKEN      - GitHub API token
#
# Output:
#   Status messages showing what was minimized

# Parse OWNER and REPO from MENTION_REPO
REPO_FULL="${MENTION_REPO:?MENTION_REPO environment variable is required}"
OWNER="${REPO_FULL%/*}"
REPO="${REPO_FULL#*/}"
PR_NUMBER="${MENTION_PR_NUMBER:?MENTION_PR_NUMBER environment variable is required}"

echo "Fetching comments and reviews for PR #${PR_NUMBER}..."

QUERY='
query($owner: String!, $repo: String!, $prNumber: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $prNumber) {
      comments(first: 100) {
        nodes {
          id
          author { login }
          createdAt
          isMinimized
        }
      }
      reviews(first: 100) {
        nodes {
          id
          author { login }
          createdAt
          comments(first: 100) {
            nodes {
              id
              author { login }
              createdAt
              isMinimized
            }
          }
        }
      }
    }
  }
}'

RESPONSE=$(gh api graphql -f query="$QUERY" -f owner="$OWNER" -f repo="$REPO" -F prNumber="$PR_NUMBER")

TO_MINIMIZE=$(echo "$RESPONSE" | jq -r '
  # Extract all comments with their metadata
  # Note: reviews.nodes are NOT included because PullRequestReview objects
  # do not have isMinimized field in the GraphQL schema (only their comments do)
  [
    (.data.repository.pullRequest.comments.nodes // []) +
    (.data.repository.pullRequest.reviews.nodes // [] | map(.comments.nodes // []) | add // [])
  ] | add // []
  # Filter out already minimized and null authors
  | map(select(.isMinimized == false and .author != null))
  # Group by author login
  | group_by(.author.login)
  # For each author, sort by createdAt and take all but the last
  | map(sort_by(.createdAt) | .[:-1])
  # Flatten and extract IDs
  | add // []
  | map(.id)
  | .[]
')

MINIMIZED_COUNT=0
for ID in $TO_MINIMIZE; do
  echo "Minimizing comment/review: $ID"
  MUTATION='
    mutation($subjectId: ID!) {
      minimizeComment(input: {
        subjectId: $subjectId,
        classifier: OUTDATED
      }) {
        minimizedComment {
          isMinimized
        }
      }
    }'
  if ! gh api graphql -f query="$MUTATION" -f subjectId="$ID" --silent; then
    echo "Warning: Failed to minimize $ID" >&2
  else
    MINIMIZED_COUNT=$((MINIMIZED_COUNT + 1))
  fi
done

echo "Successfully minimized $MINIMIZED_COUNT comments/reviews"
echo "Kept the most recent comment/review from each user visible"
