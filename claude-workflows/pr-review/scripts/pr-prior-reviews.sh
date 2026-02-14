#!/bin/bash
# pr-prior-reviews.sh - Fetch prior review submissions on a PR
#
# Shows review bodies (the summary text submitted with each review) so that
# subsequent reviews can avoid repeating points already made.
#
# This is DIFFERENT from pr-existing-comments.sh which fetches inline review
# threads (comments on specific lines). This script fetches the top-level
# review summaries submitted via "Submit review".
#
# Usage:
#   pr-prior-reviews.sh            - Show all prior reviews with bodies
#
# Output: Chronological list of prior reviews showing author, verdict,
# timestamp, and body text. Reviews with empty bodies are skipped.
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO       - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER  - Pull request number

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"

# Fetch reviews via REST API (includes review bodies, which GraphQL reviewThreads does not)
REVIEWS=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" --paginate --jq '
  [.[] | select(.body != null and .body != "") | {
    user: .user.login,
    state: .state,
    submitted_at: .submitted_at,
    body: .body
  }]
')

if [ -z "$REVIEWS" ] || [ "$REVIEWS" = "[]" ] || [ "$REVIEWS" = "null" ]; then
  echo "No prior reviews with body text found."
  exit 0
fi

REVIEW_COUNT=$(echo "$REVIEWS" | jq 'length')

if [ "$REVIEW_COUNT" -eq 0 ]; then
  echo "No prior reviews with body text found."
  exit 0
fi

echo "Prior reviews: ${REVIEW_COUNT} with body text"
echo ""

# Strip the standard footer from review bodies to reduce noise
# The footer starts with "---\n[Why is Claude responding?]"
FOOTER_PATTERN='---[[:space:]]*\\[Why is Claude responding'

echo "$REVIEWS" | jq -r --arg footer "$FOOTER_PATTERN" '
  .[] |
  "### " + .user + " — " + .state + " (" + .submitted_at + ")" + "\n" +
  (.body | split("\n---\n[Why is Claude responding?]") | .[0]) +
  "\n"
'
