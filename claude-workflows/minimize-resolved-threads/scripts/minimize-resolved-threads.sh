#!/usr/bin/env bash
set -euo pipefail

REPO="${MINIMIZE_REVIEW_REPO:?MINIMIZE_REVIEW_REPO environment variable is required}"
PR_NUMBER="${MINIMIZE_REVIEW_PR_NUMBER:?MINIMIZE_REVIEW_PR_NUMBER environment variable is required}"
AUTHOR_LOGINS="${MINIMIZE_REVIEW_AUTHOR_LOGINS:-github-actions[bot]}"
DRY_RUN="${MINIMIZE_REVIEW_DRY_RUN:-false}"

AUTHOR_LOGINS_CLEAN="$(echo "$AUTHOR_LOGINS" | tr -d ' ')"
if [ -z "$AUTHOR_LOGINS_CLEAN" ]; then
  echo "MINIMIZE_REVIEW_AUTHOR_LOGINS must not be empty." >&2
  exit 1
fi

OWNER="${REPO%/*}"
REPO_NAME="${REPO#*/}"

IFS=',' read -r -a AUTHOR_ARRAY <<< "$AUTHOR_LOGINS_CLEAN"
AUTHOR_JSON="$(printf '%s\n' "${AUTHOR_ARRAY[@]}" | jq -R . | jq -s .)"

THREADS=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $prNumber) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            comments(first: 50) {
              nodes {
                id
                isMinimized
                author { login }
              }
            }
          }
        }
      }
    }
  }' -F owner="$OWNER" \
     -F repo="$REPO_NAME" \
     -F prNumber="$PR_NUMBER" \
     --jq '.data.repository.pullRequest.reviewThreads.nodes')

if [ -z "$THREADS" ] || [ "$THREADS" = "null" ]; then
  echo "No review threads found."
  exit 0
fi

TARGETS=$(echo "$THREADS" | jq --argjson authors "$AUTHOR_JSON" '
  [ .[] |
    select(.isResolved == true) |
    select(.comments.nodes | length > 0) |
    .comments.nodes[0] as $root |
    select($root.author.login != null) |
    select($authors | index($root.author.login)) |
    select($root.isMinimized != true) |
    {threadId: .id, commentId: $root.id, author: $root.author.login}
  ]')

COUNT=$(echo "$TARGETS" | jq 'length')
if [ "$COUNT" -eq 0 ]; then
  echo "No resolved review threads to minimize."
  exit 0
fi

echo "Minimizing ${COUNT} resolved review thread(s) authored by ${AUTHOR_LOGINS_CLEAN}..."

if [ "$DRY_RUN" = "true" ]; then
  echo "$TARGETS" | jq -r '.[] | "- thread " + .threadId + " comment " + .commentId + " author " + .author'
  exit 0
fi

echo "$TARGETS" | jq -r '.[].commentId' | while read -r COMMENT_ID; do
  [ -n "$COMMENT_ID" ] || continue
  gh api graphql -f query='
    mutation($commentId: ID!) {
      minimizeComment(input: {subjectId: $commentId, classifier: RESOLVED}) {
        minimizedComment {
          isMinimized
        }
      }
    }' -f commentId="$COMMENT_ID" --jq '.data.minimizeComment.minimizedComment.isMinimized' > /dev/null
done

echo "✓ Minimized ${COUNT} resolved review thread(s)."
