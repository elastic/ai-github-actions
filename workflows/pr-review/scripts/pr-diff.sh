#!/bin/bash
# pr-diff.sh - Show changed files or diff for a specific file
#
# Usage: 
#   pr-diff.sh           - List all changed files
#   pr-diff.sh <file>    - Show diff for a specific file
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO       - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER  - Pull request number

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"

FILE="$1"

if [ -z "$FILE" ]; then
  echo "Files changed in this PR:"
  echo ""
  gh api "repos/${REPO}/pulls/${PR_NUMBER}/files" --paginate --jq '.[] | "  \(.filename) (+\(.additions)/-\(.deletions))"'
else
  PATCH=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/files" --paginate --jq ".[] | select(.filename==\"${FILE}\") | .patch")
  
  if [ -z "$PATCH" ]; then
    echo "Error: File '${FILE}' not found in PR diff"
    echo ""
    echo "Files changed in this PR:"
    gh api "repos/${REPO}/pulls/${PR_NUMBER}/files" --paginate --jq '.[].filename'
    exit 1
  fi
  
  echo "Diff for ${FILE}:"
  echo ""
  echo "$PATCH"
fi
