#!/bin/bash
# pr-comment.sh - Queue an inline review comment for the PR review
#
# Usage:
#   pr-comment.sh <file> <line-number> <comment-body>
#   pr-comment.sh <file> <line-number> -f <body-file>
#
# Examples:
#   pr-comment.sh src/main.go 42 "This variable is unused"
#   pr-comment.sh src/main.go 42 -f /tmp/comment.md
#
# The -f option reads the comment body from a file, which is useful for:
#   - Multi-line comments
#   - Comments with special characters (quotes, backticks, etc.)
#   - Code suggestions with complex formatting
#
# This script validates the comment location and caches it for later submission.
# Comments are stored in PR_REVIEW_COMMENTS_FILE and submitted when pr-review.sh runs.
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO          - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER     - Pull request number
#   PR_REVIEW_COMMENTS_FILE - File to cache comments (default: /tmp/pr-review-comments.json)

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"
COMMENTS_FILE="${PR_REVIEW_COMMENTS_FILE:-/tmp/pr-review-comments.json}"

# Parse arguments
FILE="$1"
LINE="$2"
shift 2 2>/dev/null || true

# Check if using -f flag to read body from file
if [ "$1" = "-f" ]; then
  BODY_FILE="$2"
  if [ -z "$BODY_FILE" ]; then
    echo "Error: -f flag requires a file path"
    echo "Usage: pr-comment.sh <file> <line-number> -f <body-file>"
    exit 1
  fi
  if [ ! -f "$BODY_FILE" ]; then
    echo "Error: Body file not found: $BODY_FILE"
    exit 1
  fi
  BODY=$(cat "$BODY_FILE")
else
  BODY="$*"
fi

if [ -z "$FILE" ] || [ -z "$LINE" ] || [ -z "$BODY" ]; then
  echo "Usage:"
  echo "  pr-comment.sh <file> <line-number> <comment-body>"
  echo "  pr-comment.sh <file> <line-number> -f <body-file>"
  echo ""
  echo "Examples:"
  echo "  pr-comment.sh src/main.go 42 'This variable is unused'"
  echo "  pr-comment.sh src/main.go 42 -f /tmp/comment.md"
  exit 1
fi

# Validate line is a number
if ! [[ "$LINE" =~ ^[0-9]+$ ]]; then
  echo "Error: Line number must be a positive integer, got: $LINE"
  exit 1
fi

# Get the diff for this file to validate the comment location
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

# Verify the line exists in the diff
# We need to check if the line number corresponds to a line in the new file (side: RIGHT)
LINE_IN_DIFF=$(echo "$PATCH" | awk -v target_line="$LINE" '
BEGIN { current_line = 0; found = 0 }
/^@@/ {
  # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
  # Extract the new file start line number after the +
  line = $0
  gsub(/.*\+/, "", line)      # Remove everything up to and including +
  gsub(/[^0-9].*/, "", line)  # Remove everything after the number
  current_line = line - 1     # Will be incremented for non-deletion lines
  next
}
{
  if (substr($0, 1, 1) != "-") {
    # Not a deletion, so this line exists in the new file
    current_line++
    if (current_line == target_line) {
      found = 1
      exit
    }
  }
}
END { if (found) print "1"; else print "0" }
')

if [ "$LINE_IN_DIFF" != "1" ]; then
  echo "Error: Line ${LINE} not found in the diff for '${FILE}'"
  echo ""
  echo "Note: You can only comment on lines that appear in the diff (added, modified, or context lines)"
  echo ""
  echo "First 50 lines of diff for this file:"
  echo "$PATCH" | head -50
  exit 1
fi

# Initialize comments file if it doesn't exist
if [ ! -f "${COMMENTS_FILE}" ]; then
  echo "[]" > "${COMMENTS_FILE}"
fi

# Append standard footer to the comment
FOOTER='
---
*Comment by Claude Code* | 🚀 if perfect, 👍 if helpful, 👎 if not | Type `@claude` to interact further | [What is this?](https://ela.st/github-ai-tools)'

BODY_WITH_FOOTER="${BODY}${FOOTER}"

# Create the comment JSON object
# Use jq to safely handle special characters in the body
COMMENT_JSON=$(jq -n \
  --arg path "$FILE" \
  --argjson line "$LINE" \
  --arg side "RIGHT" \
  --arg body "$BODY_WITH_FOOTER" \
  '{path: $path, line: $line, side: $side, body: $body}')

# Append the comment to the comments file
# Read existing comments, add new one, write back
jq --argjson new_comment "$COMMENT_JSON" '. += [$new_comment]' "${COMMENTS_FILE}" > "${COMMENTS_FILE}.tmp" \
  && mv "${COMMENTS_FILE}.tmp" "${COMMENTS_FILE}"

echo "✓ Queued review comment for ${FILE}:${LINE}"
echo "  Comment will be submitted with pr-review.sh"
