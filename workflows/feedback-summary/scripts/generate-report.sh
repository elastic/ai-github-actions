#!/bin/bash
# generate-report.sh - Generate markdown report from feedback JSON
#
# Usage: generate-report.sh <feedback-json-file> [output-file]
# Example: generate-report.sh /tmp/feedback-data.json /tmp/feedback-report.md
#
# If output-file is not provided, outputs to stdout

set -e

INPUT_FILE="${1:?Usage: generate-report.sh <feedback-json-file> [output-file]}"
OUTPUT_FILE="${2:-}"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: Input file not found: $INPUT_FILE" >&2
  exit 1
fi

FEEDBACK=$(cat "$INPUT_FILE")

# Extract metadata
REPO=$(echo "$FEEDBACK" | jq -r '.metadata.repo')
DAYS=$(echo "$FEEDBACK" | jq -r '.metadata.days')
SINCE=$(echo "$FEEDBACK" | jq -r '.metadata.since')
GENERATED=$(echo "$FEEDBACK" | jq -r '.metadata.generated_at')
BOT_PATTERN=$(echo "$FEEDBACK" | jq -r '.metadata.bot_pattern')

# Extract summary stats
TOTAL=$(echo "$FEEDBACK" | jq '.summary.total_interactions')
POSITIVE=$(echo "$FEEDBACK" | jq '.summary.positive_reactions')
NEGATIVE=$(echo "$FEEDBACK" | jq '.summary.negative_reactions')
NO_REACTION=$(echo "$FEEDBACK" | jq '.summary.no_reactions')

ROCKETS=$(echo "$FEEDBACK" | jq '.summary.reaction_counts.rocket')
THUMBSUP=$(echo "$FEEDBACK" | jq '.summary.reaction_counts.thumbsup')
THUMBSDOWN=$(echo "$FEEDBACK" | jq '.summary.reaction_counts.thumbsdown')
HEARTS=$(echo "$FEEDBACK" | jq '.summary.reaction_counts.heart')
CONFUSED=$(echo "$FEEDBACK" | jq '.summary.reaction_counts.confused')

# Calculate satisfaction rate
TOTAL_REACTIONS=$((ROCKETS + THUMBSUP + THUMBSDOWN + HEARTS + CONFUSED))
if [ "$TOTAL_REACTIONS" -gt 0 ]; then
  POSITIVE_REACTIONS=$((ROCKETS + THUMBSUP + HEARTS))
  # Use awk for floating point math (more portable than bc)
  SATISFACTION=$(awk "BEGIN {printf \"%.1f\", $POSITIVE_REACTIONS * 100 / $TOTAL_REACTIONS}")
  SATISFACTION_SUFFIX="%"
else
  SATISFACTION="N/A"
  SATISFACTION_SUFFIX=""
fi

# Generate the report
generate_report() {
  cat << EOF
## AI Agent Feedback Summary

**Repository:** ${REPO}
**Period:** Last ${DAYS} days (since ${SINCE})
**Generated:** ${GENERATED}

### Overview

| Metric | Value |
|--------|-------|
| Total Interactions | ${TOTAL} |
| With Positive Reactions | ${POSITIVE} |
| With Negative Reactions | ${NEGATIVE} |
| No Reactions | ${NO_REACTION} |
| **Satisfaction Rate** | **${SATISFACTION}${SATISFACTION_SUFFIX}** |

### Reaction Breakdown

| Reaction | Count | Meaning |
|----------|-------|---------|
| 🚀 Rocket | ${ROCKETS} | Perfect |
| 👍 Thumbs Up | ${THUMBSUP} | Helpful |
| ❤️ Heart | ${HEARTS} | Appreciated |
| 👎 Thumbs Down | ${THUMBSDOWN} | Not Helpful |
| 😕 Confused | ${CONFUSED} | Confusing |

EOF

  # Add negative interactions table if any exist
  if [ "$NEGATIVE" -gt 0 ]; then
    echo "### Interactions with Negative Feedback"
    echo ""
    echo "| Type | Location | Reactions | Preview |"
    echo "|------|----------|-----------|---------|"
    
    echo "$FEEDBACK" | jq -r '
      .items[] 
      | select(.reactions.thumbsdown > 0 or .reactions.confused > 0) 
      | "| \(.type) | [#\(.context_num)](\(.html_url)) | 👎\(.reactions.thumbsdown) 😕\(.reactions.confused) | \(.body_preview[0:80] | gsub("\n"; " ") | gsub("\\|"; "\\|"))... |"
    '
    echo ""
  fi

  # Add recent interactions table
  echo "### Recent Interactions (Last 10)"
  echo ""
  echo "| Date | Type | Location | Reactions |"
  echo "|------|------|----------|-----------|"
  
  echo "$FEEDBACK" | jq -r '
    [.items | sort_by(.created_at) | reverse | .[:10] | .[] 
    | "| \(.created_at[0:10]) | \(.type) | [#\(.context_num)](\(.html_url)) | 🚀\(.reactions.rocket) 👍\(.reactions.thumbsup) 👎\(.reactions.thumbsdown) |"
    ] | join("\n")
  '
  echo ""

  # Add interaction breakdown by type
  echo "### Breakdown by Interaction Type"
  echo ""
  echo "| Type | Count |"
  echo "|------|-------|"
  
  echo "$FEEDBACK" | jq -r '
    .items | group_by(.type) | .[] 
    | "| \(.[0].type) | \(length) |"
  '
  echo ""
}

# Output to file or stdout
if [ -n "$OUTPUT_FILE" ]; then
  generate_report > "$OUTPUT_FILE"
  echo "Report written to: $OUTPUT_FILE" >&2
else
  generate_report
fi
