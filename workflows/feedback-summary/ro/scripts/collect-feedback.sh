#!/bin/bash
# collect-feedback.sh - Collect reactions on AI agent comments
#
# Usage: collect-feedback.sh [days]
# Example: collect-feedback.sh 7
#
# Outputs JSON with feedback data for AI agent comments
#
# Environment variables:
#   FEEDBACK_REPO       - Repository (owner/repo)
#   FEEDBACK_BOT_PATTERN - Regex pattern to match bot usernames (default matches common AI bots)
#   FEEDBACK_DAYS       - Number of days to look back (default: 7)
#
# The bot pattern is a regex. Examples:
#   "claude"                           - matches "claude", "Claude", etc.
#   "github-actions\\[bot\\]"          - matches github-actions[bot]
#   "claude|github-actions\\[bot\\]"   - matches either

set -e

REPO="${FEEDBACK_REPO:?FEEDBACK_REPO environment variable is required}"
# Default pattern matches common AI agent bot accounts
BOT_PATTERN="${FEEDBACK_BOT_PATTERN:-claude|github-actions\\[bot\\]|copilot\\[bot\\]}"
DAYS="${1:-${FEEDBACK_DAYS:-7}}"

# Calculate date threshold
if [[ "$OSTYPE" == "darwin"* ]]; then
  SINCE_DATE=$(date -v-${DAYS}d +%Y-%m-%dT%H:%M:%SZ)
else
  SINCE_DATE=$(date -d "${DAYS} days ago" +%Y-%m-%dT%H:%M:%SZ)
fi

echo "Collecting feedback for bot pattern '${BOT_PATTERN}' in ${REPO} since ${SINCE_DATE}" >&2

# Initialize results
RESULTS="[]"

# Function to get reactions for a comment
get_reactions() {
  local comment_url="$1"
  gh api "${comment_url}/reactions" --jq '[.[] | .content]' 2>/dev/null || echo "[]"
}

# Function to categorize reactions
categorize_reactions() {
  local reactions="$1"
  local rocket=$(echo "$reactions" | jq '[.[] | select(. == "rocket")] | length')
  local thumbsup=$(echo "$reactions" | jq '[.[] | select(. == "+1")] | length')
  local thumbsdown=$(echo "$reactions" | jq '[.[] | select(. == "-1")] | length')
  local heart=$(echo "$reactions" | jq '[.[] | select(. == "heart")] | length')
  local confused=$(echo "$reactions" | jq '[.[] | select(. == "confused")] | length')
  
  echo "{\"rocket\": $rocket, \"thumbsup\": $thumbsup, \"thumbsdown\": $thumbsdown, \"heart\": $heart, \"confused\": $confused}"
}

# Search for issue comments by the bot
echo "Searching issue comments..." >&2
ISSUE_COMMENTS=$(gh api "repos/${REPO}/issues/comments" \
  --paginate \
  --jq ".[] | select(.user.login | test(\"${BOT_PATTERN}\"; \"i\")) | select(.created_at >= \"${SINCE_DATE}\") | {id: .id, url: .url, html_url: .html_url, issue_url: .issue_url, body: .body[0:500], created_at: .created_at, user: .user.login}" 2>/dev/null || echo "")

# Process issue comments
if [ -n "$ISSUE_COMMENTS" ]; then
  while IFS= read -r comment; do
    [ -z "$comment" ] && continue
    
    COMMENT_ID=$(echo "$comment" | jq -r '.id')
    COMMENT_URL=$(echo "$comment" | jq -r '.url')
    HTML_URL=$(echo "$comment" | jq -r '.html_url')
    ISSUE_URL=$(echo "$comment" | jq -r '.issue_url')
    BODY=$(echo "$comment" | jq -r '.body')
    CREATED=$(echo "$comment" | jq -r '.created_at')
    
    # Extract issue/PR number from URL
    ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
    
    # Get reactions
    REACTIONS=$(gh api "repos/${REPO}/issues/comments/${COMMENT_ID}/reactions" --jq '[.[] | .content]' 2>/dev/null || echo "[]")
    REACTION_COUNTS=$(categorize_reactions "$REACTIONS")
    
    # Determine context type (issue or PR)
    CONTEXT_TYPE="issue"
    if gh api "repos/${REPO}/pulls/${ISSUE_NUM}" >/dev/null 2>&1; then
      CONTEXT_TYPE="pr"
    fi
    
    # Add to results
    RESULTS=$(echo "$RESULTS" | jq --argjson reactions "$REACTION_COUNTS" \
      --arg html_url "$HTML_URL" \
      --arg context_type "$CONTEXT_TYPE" \
      --arg context_num "$ISSUE_NUM" \
      --arg created "$CREATED" \
      --arg body "$BODY" \
      --arg type "issue_comment" \
      '. += [{
        type: $type,
        context_type: $context_type,
        context_num: ($context_num | tonumber),
        html_url: $html_url,
        created_at: $created,
        body_preview: $body,
        reactions: $reactions
      }]')
    
  done <<< "$ISSUE_COMMENTS"
fi

# Search for PR review comments by the bot
echo "Searching PR review comments..." >&2
PR_COMMENTS=$(gh api "repos/${REPO}/pulls/comments" \
  --paginate \
  --jq ".[] | select(.user.login | test(\"${BOT_PATTERN}\"; \"i\")) | select(.created_at >= \"${SINCE_DATE}\") | {id: .id, url: .url, html_url: .html_url, pull_request_url: .pull_request_url, body: .body[0:500], created_at: .created_at, user: .user.login}" 2>/dev/null || echo "")

# Process PR review comments
if [ -n "$PR_COMMENTS" ]; then
  while IFS= read -r comment; do
    [ -z "$comment" ] && continue
    
    COMMENT_ID=$(echo "$comment" | jq -r '.id')
    HTML_URL=$(echo "$comment" | jq -r '.html_url')
    PR_URL=$(echo "$comment" | jq -r '.pull_request_url')
    BODY=$(echo "$comment" | jq -r '.body')
    CREATED=$(echo "$comment" | jq -r '.created_at')
    
    # Extract PR number from URL
    PR_NUM=$(echo "$PR_URL" | grep -oE '[0-9]+$')
    
    # Get reactions
    REACTIONS=$(gh api "repos/${REPO}/pulls/comments/${COMMENT_ID}/reactions" --jq '[.[] | .content]' 2>/dev/null || echo "[]")
    REACTION_COUNTS=$(categorize_reactions "$REACTIONS")
    
    # Add to results
    RESULTS=$(echo "$RESULTS" | jq --argjson reactions "$REACTION_COUNTS" \
      --arg html_url "$HTML_URL" \
      --arg context_num "$PR_NUM" \
      --arg created "$CREATED" \
      --arg body "$BODY" \
      --arg type "pr_review_comment" \
      '. += [{
        type: $type,
        context_type: "pr",
        context_num: ($context_num | tonumber),
        html_url: $html_url,
        created_at: $created,
        body_preview: $body,
        reactions: $reactions
      }]')
    
  done <<< "$PR_COMMENTS"
fi

# Search for PR reviews by the bot
echo "Searching PR reviews..." >&2
# Get list of recent PRs first
RECENT_PRS=$(gh api "repos/${REPO}/pulls?state=all&sort=updated&direction=desc&per_page=50" --jq '.[].number' 2>/dev/null || echo "")

for PR_NUM in $RECENT_PRS; do
  REVIEWS=$(gh api "repos/${REPO}/pulls/${PR_NUM}/reviews" \
    --jq ".[] | select(.user.login | test(\"${BOT_PATTERN}\"; \"i\")) | select(.submitted_at >= \"${SINCE_DATE}\") | {id: .id, html_url: .html_url, body: .body[0:500], submitted_at: .submitted_at, state: .state}" 2>/dev/null || echo "")
  
  if [ -n "$REVIEWS" ]; then
    while IFS= read -r review; do
      [ -z "$review" ] && continue
      
      REVIEW_ID=$(echo "$review" | jq -r '.id')
      HTML_URL=$(echo "$review" | jq -r '.html_url')
      BODY=$(echo "$review" | jq -r '.body')
      SUBMITTED=$(echo "$review" | jq -r '.submitted_at')
      STATE=$(echo "$review" | jq -r '.state')
      
      # Reviews don't have reactions API, so we'll track them without reactions
      REACTION_COUNTS='{"rocket": 0, "thumbsup": 0, "thumbsdown": 0, "heart": 0, "confused": 0}'
      
      # Add to results
      RESULTS=$(echo "$RESULTS" | jq --argjson reactions "$REACTION_COUNTS" \
        --arg html_url "$HTML_URL" \
        --arg context_num "$PR_NUM" \
        --arg created "$SUBMITTED" \
        --arg body "$BODY" \
        --arg state "$STATE" \
        --arg type "pr_review" \
        '. += [{
          type: $type,
          context_type: "pr",
          context_num: ($context_num | tonumber),
          html_url: $html_url,
          created_at: $created,
          body_preview: $body,
          review_state: $state,
          reactions: $reactions
        }]')
      
    done <<< "$REVIEWS"
  fi
done

# Calculate summary statistics
TOTAL=$(echo "$RESULTS" | jq 'length')
TOTAL_ROCKET=$(echo "$RESULTS" | jq '[.[].reactions.rocket] | add // 0')
TOTAL_THUMBSUP=$(echo "$RESULTS" | jq '[.[].reactions.thumbsup] | add // 0')
TOTAL_THUMBSDOWN=$(echo "$RESULTS" | jq '[.[].reactions.thumbsdown] | add // 0')
TOTAL_HEART=$(echo "$RESULTS" | jq '[.[].reactions.heart] | add // 0')
TOTAL_CONFUSED=$(echo "$RESULTS" | jq '[.[].reactions.confused] | add // 0')

# Items with any positive reaction
POSITIVE_ITEMS=$(echo "$RESULTS" | jq '[.[] | select(.reactions.rocket > 0 or .reactions.thumbsup > 0 or .reactions.heart > 0)] | length')

# Items with negative reaction
NEGATIVE_ITEMS=$(echo "$RESULTS" | jq '[.[] | select(.reactions.thumbsdown > 0 or .reactions.confused > 0)] | length')

# Items with no reaction
NO_REACTION_ITEMS=$(echo "$RESULTS" | jq '[.[] | select(.reactions.rocket == 0 and .reactions.thumbsup == 0 and .reactions.thumbsdown == 0 and .reactions.heart == 0 and .reactions.confused == 0)] | length')

# Build final output
OUTPUT=$(jq -n \
  --arg repo "$REPO" \
  --arg bot_pattern "$BOT_PATTERN" \
  --arg since "$SINCE_DATE" \
  --arg days "$DAYS" \
  --argjson total "$TOTAL" \
  --argjson positive_items "$POSITIVE_ITEMS" \
  --argjson negative_items "$NEGATIVE_ITEMS" \
  --argjson no_reaction_items "$NO_REACTION_ITEMS" \
  --argjson total_rocket "$TOTAL_ROCKET" \
  --argjson total_thumbsup "$TOTAL_THUMBSUP" \
  --argjson total_thumbsdown "$TOTAL_THUMBSDOWN" \
  --argjson total_heart "$TOTAL_HEART" \
  --argjson total_confused "$TOTAL_CONFUSED" \
  --argjson items "$RESULTS" \
  '{
    metadata: {
      repo: $repo,
      bot_pattern: $bot_pattern,
      since: $since,
      days: ($days | tonumber),
      generated_at: (now | todate)
    },
    summary: {
      total_interactions: $total,
      positive_reactions: $positive_items,
      negative_reactions: $negative_items,
      no_reactions: $no_reaction_items,
      reaction_counts: {
        rocket: $total_rocket,
        thumbsup: $total_thumbsup,
        thumbsdown: $total_thumbsdown,
        heart: $total_heart,
        confused: $total_confused
      }
    },
    items: $items
  }')

echo "$OUTPUT"
