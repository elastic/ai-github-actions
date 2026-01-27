#!/bin/bash
# pr-review.sh - Submit a PR review (approve, request changes, or comment)
#
# Usage: pr-review.sh <APPROVE|REQUEST_CHANGES|COMMENT> [review-body]
# Example: pr-review.sh REQUEST_CHANGES "Please fix the issues noted above"
#
# This script creates and submits a review with any queued inline comments.
# Comments are read from PR_REVIEW_COMMENTS_FILE (created by pr-comment.sh).
#
# The review body can contain special characters (backticks, dollar signs, etc.)
# and will be safely passed to the GitHub API without shell interpretation.
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO          - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER     - Pull request number
#   PR_REVIEW_HEAD_SHA      - HEAD commit SHA
#   PR_REVIEW_COMMENTS_FILE - File containing queued comments (default: /tmp/pr-review-comments.json)

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"
HEAD_SHA="${PR_REVIEW_HEAD_SHA:?PR_REVIEW_HEAD_SHA environment variable is required}"
COMMENTS_FILE="${PR_REVIEW_COMMENTS_FILE:-/tmp/pr-review-comments.json}"

# Arguments
EVENT="$1"
shift 2>/dev/null || true

# Read body from remaining arguments
# Join all remaining arguments with spaces, preserving the string as-is
BODY="$*"

if [ -z "$EVENT" ]; then
  echo "Usage: pr-review.sh <APPROVE|REQUEST_CHANGES|COMMENT> [review-body]"
  echo "Example: pr-review.sh REQUEST_CHANGES 'Please fix the issues noted in the inline comments'"
  exit 1
fi

# Validate event type
case "$EVENT" in
  APPROVE|REQUEST_CHANGES|COMMENT)
    ;;
  *)
    echo "Error: Invalid event type '${EVENT}'"
    echo "Must be one of: APPROVE, REQUEST_CHANGES, COMMENT"
    exit 1
    ;;
esac

# Read queued comments if any exist
COMMENTS="[]"
if [ -f "${COMMENTS_FILE}" ]; then
  COMMENTS=$(cat "${COMMENTS_FILE}")
  COMMENT_COUNT=$(echo "$COMMENTS" | jq 'length')
  if [ "$COMMENT_COUNT" -gt 0 ]; then
    echo "Found ${COMMENT_COUNT} queued inline comment(s)"
  fi
else
  COMMENT_COUNT=0
fi

# Build the review request JSON
# Use jq to safely construct the JSON with all special characters handled
REVIEW_JSON=$(jq -n \
  --arg commit_id "$HEAD_SHA" \
  --arg event "$EVENT" \
  --arg body "$BODY" \
  --argjson comments "$COMMENTS" \
  '{
    commit_id: $commit_id,
    event: $event,
    comments: $comments
  } + (if $body != "" then {body: $body} else {} end)')

echo "Submitting ${EVENT} review..."

# Create and submit the review in one API call
# Use a temp file to safely pass the JSON body
TEMP_JSON=$(mktemp)
trap "rm -f ${TEMP_JSON}" EXIT
echo "$REVIEW_JSON" > "${TEMP_JSON}"

RESPONSE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
  -X POST \
  --input "${TEMP_JSON}" 2>&1) || {
  echo "Error submitting review:"
  echo "$RESPONSE"
  exit 1
}

# Clean up the comments file
if [ -f "${COMMENTS_FILE}" ]; then
  rm -f "${COMMENTS_FILE}"
fi

REVIEW_URL=$(echo "$RESPONSE" | jq -r '.html_url // empty')
REVIEW_STATE=$(echo "$RESPONSE" | jq -r '.state // empty')

if [ -n "$REVIEW_URL" ]; then
  echo "✓ Review submitted (${REVIEW_STATE}): ${REVIEW_URL}"
  if [ "$COMMENT_COUNT" -gt 0 ]; then
    echo "  Included ${COMMENT_COUNT} inline comment(s)"
  fi
else
  echo "✓ Review submitted successfully"
fi
