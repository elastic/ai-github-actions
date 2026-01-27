#!/bin/bash
# pr-review.sh - Submit a PR review (approve, request changes, or comment)
#
# Usage: pr-review.sh <APPROVE|REQUEST_CHANGES|COMMENT> [review-body]
# Example: pr-review.sh REQUEST_CHANGES "Please fix the issues noted above"
#
# The review body can contain special characters (backticks, dollar signs, etc.)
# and will be safely passed to the GitHub API without shell interpretation.
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO       - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER  - Pull request number
#   PR_REVIEW_HEAD_SHA   - HEAD commit SHA

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"
HEAD_SHA="${PR_REVIEW_HEAD_SHA:?PR_REVIEW_HEAD_SHA environment variable is required}"

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

echo "Submitting ${EVENT} review..."

# Build the API call
# Use a temporary file to safely pass the body to gh api to avoid shell interpretation issues
TEMP_BODY=$(mktemp)
trap "rm -f ${TEMP_BODY}" EXIT

if [ -n "$BODY" ]; then
  # Write body to temp file to avoid shell interpretation of special characters
  printf '%s' "$BODY" > "${TEMP_BODY}"
  
  RESPONSE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
    -X POST \
    -f commit_id="${HEAD_SHA}" \
    -f event="${EVENT}" \
    --field body=@"${TEMP_BODY}" 2>&1) || {
    echo "Error submitting review:"
    echo "$RESPONSE"
    exit 1
  }
else
  RESPONSE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
    -X POST \
    -f commit_id="${HEAD_SHA}" \
    -f event="${EVENT}" 2>&1) || {
    echo "Error submitting review:"
    echo "$RESPONSE"
    exit 1
  }
fi

REVIEW_URL=$(echo "$RESPONSE" | jq -r '.html_url // empty')
if [ -n "$REVIEW_URL" ]; then
  echo "✓ Review submitted: ${REVIEW_URL}"
else
  echo "✓ Review submitted successfully"
fi
