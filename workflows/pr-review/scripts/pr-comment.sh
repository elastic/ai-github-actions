#!/bin/bash
# pr-comment.sh - Add an inline comment to a specific line in a PR
#
# Usage: pr-comment.sh <file> <line-number> <comment-body>
# Example: pr-comment.sh src/main.go 42 "This variable is unused"
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
FILE="$1"
LINE="$2"
shift 2 2>/dev/null || true
BODY="$*"

if [ -z "$FILE" ] || [ -z "$LINE" ] || [ -z "$BODY" ]; then
  echo "Usage: pr-comment.sh <file> <line-number> <comment-body>"
  echo "Example: pr-comment.sh src/main.go 42 'This variable is unused'"
  exit 1
fi

# Validate line is a number
if ! [[ "$LINE" =~ ^[0-9]+$ ]]; then
  echo "Error: Line number must be a positive integer, got: $LINE"
  exit 1
fi

# Get the diff for this file
DIFF_DATA=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/files" --paginate --jq ".[] | select(.filename==\"${FILE}\")")

if [ -z "$DIFF_DATA" ]; then
  echo "Error: File '${FILE}' not found in PR diff"
  echo ""
  echo "Files changed in this PR:"
  gh api "repos/${REPO}/pulls/${PR_NUMBER}/files" --paginate --jq '.[].filename'
  exit 1
fi

PATCH=$(echo "$DIFF_DATA" | jq -r '.patch // empty')

if [ -z "$PATCH" ]; then
  echo "Error: No patch data for file '${FILE}' (file may be binary or too large)"
  exit 1
fi

# Calculate the position from line number
# Position is 1-indexed from the start of the diff hunk
# We need to find which line in the patch corresponds to the requested line number
POSITION=$(echo "$PATCH" | awk -v target_line="$LINE" '
BEGIN { position = 0; current_line = 0; found = 0 }
/^@@/ {
  # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
  match($0, /\+([0-9]+)/, arr)
  current_line = arr[1] - 1  # Will be incremented for non-deletion lines
  position++  # Count the @@ line itself
  next
}
{
  position++
  if (substr($0, 1, 1) != "-") {
    # Not a deletion, so this line exists in the new file
    current_line++
    if (current_line == target_line) {
      print position
      found = 1
      exit
    }
  }
}
END { if (!found) print "" }
')

if [ -z "$POSITION" ]; then
  echo "Error: Line ${LINE} not found in the diff for '${FILE}'"
  echo ""
  echo "Note: You can only comment on lines that appear in the diff (added, modified, or context lines)"
  echo ""
  echo "First 50 lines of diff for this file:"
  echo "$PATCH" | head -50
  exit 1
fi

echo "Adding comment to ${FILE}:${LINE} (diff position: ${POSITION})"

# Post the comment
RESPONSE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/comments" \
  -X POST \
  -f commit_id="${HEAD_SHA}" \
  -f path="${FILE}" \
  -f position="${POSITION}" \
  --raw-field body="${BODY}" 2>&1) || {
  echo "Error posting comment:"
  echo "$RESPONSE"
  exit 1
}

COMMENT_URL=$(echo "$RESPONSE" | jq -r '.html_url // empty')
if [ -n "$COMMENT_URL" ]; then
  echo "✓ Comment added: ${COMMENT_URL}"
else
  echo "✓ Comment added successfully"
fi
