#!/bin/bash
# pr-review.sh - Submit a PR review (approve, request changes, or comment)
#
# Usage: pr-review.sh <APPROVE|REQUEST_CHANGES|COMMENT> [review-body]
# Example: pr-review.sh REQUEST_CHANGES "Please fix the issues noted above"
#
# This script creates and submits a review with any queued inline comments.
# Comments are read from individual files in PR_REVIEW_COMMENTS_DIR (created by pr-comment.sh).
#
# The review body can contain special characters (backticks, dollar signs, etc.)
# and will be safely passed to the GitHub API without shell interpretation.
#
# Environment variables (set by the composite action):
#   PR_REVIEW_REPO          - Repository (owner/repo)
#   PR_REVIEW_PR_NUMBER     - Pull request number
#   PR_REVIEW_HEAD_SHA      - HEAD commit SHA
#   PR_REVIEW_COMMENTS_DIR  - Directory containing queued comment files (default: /tmp/pr-review-comments)

set -e

# Configuration from environment
REPO="${PR_REVIEW_REPO:?PR_REVIEW_REPO environment variable is required}"
PR_NUMBER="${PR_REVIEW_PR_NUMBER:?PR_REVIEW_PR_NUMBER environment variable is required}"
HEAD_SHA="${PR_REVIEW_HEAD_SHA:?PR_REVIEW_HEAD_SHA environment variable is required}"
COMMENTS_DIR="${PR_REVIEW_COMMENTS_DIR:-/tmp/pr-review-comments}"

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

# File extension to language mapping for fenced code blocks
ext_to_lang() {
  local file="$1"
  local ext="${file##*.}"
  case "$ext" in
    go) echo "go" ;;
    py) echo "python" ;;
    js) echo "javascript" ;;
    ts) echo "typescript" ;;
    tsx) echo "tsx" ;;
    jsx) echo "jsx" ;;
    rb) echo "ruby" ;;
    rs) echo "rust" ;;
    java) echo "java" ;;
    kt|kts) echo "kotlin" ;;
    swift) echo "swift" ;;
    c|h) echo "c" ;;
    cpp|cc|cxx|hpp) echo "cpp" ;;
    cs) echo "csharp" ;;
    sh|bash|zsh) echo "bash" ;;
    yml|yaml) echo "yaml" ;;
    json) echo "json" ;;
    toml) echo "toml" ;;
    xml) echo "xml" ;;
    html|htm) echo "html" ;;
    css) echo "css" ;;
    scss) echo "scss" ;;
    sql) echo "sql" ;;
    md) echo "markdown" ;;
    dockerfile|Dockerfile) echo "dockerfile" ;;
    tf) echo "hcl" ;;
    ex|exs) echo "elixir" ;;
    php) echo "php" ;;
    lua) echo "lua" ;;
    r|R) echo "r" ;;
    pl|pm) echo "perl" ;;
    scala) echo "scala" ;;
    *) echo "" ;;
  esac
}

# Read queued comments from individual files
ALL_COMMENTS="[]"
TOTAL_COUNT=0

if [ -d "${COMMENTS_DIR}" ]; then
  COMMENT_FILES=("${COMMENTS_DIR}"/comment-*.json)

  if [ -f "${COMMENT_FILES[0]}" ]; then
    ALL_COMMENTS=$(jq -s '.' "${COMMENTS_DIR}"/comment-*.json)
    TOTAL_COUNT=$(echo "$ALL_COMMENTS" | jq 'length')
  fi
fi

# Separate below-threshold comments from actionable inline comments
# Below-threshold comments go into the review body; everything else stays inline
severity_rank() {
  case "$1" in
    critical) echo 5 ;;
    high) echo 4 ;;
    medium) echo 3 ;;
    low) echo 2 ;;
    nitpick) echo 1 ;;
    *) echo 0 ;;
  esac
}

MIN_SEVERITY="${PR_REVIEW_MIN_SEVERITY:-low}"
MIN_SEVERITY_RANK=$(severity_rank "$MIN_SEVERITY")
if [ "$MIN_SEVERITY_RANK" -eq 0 ]; then
  echo "Error: Invalid PR_REVIEW_MIN_SEVERITY '${MIN_SEVERITY}'. Must be one of: critical, high, medium, low, nitpick"
  exit 1
fi

COMMENTS=$(echo "$ALL_COMMENTS" | jq --argjson min_rank "$MIN_SEVERITY_RANK" '
def rank(s):
  if s=="critical" then 5
  elif s=="high" then 4
  elif s=="medium" then 3
  elif s=="low" then 2
  elif s=="nitpick" then 1
  else 0 end;
[.[] | select(rank(._meta.severity) >= $min_rank) | del(._meta)]')
COMMENT_COUNT=$(echo "$COMMENTS" | jq 'length')

LOWER_SEVERITY=$(echo "$ALL_COMMENTS" | jq --argjson min_rank "$MIN_SEVERITY_RANK" '
def rank(s):
  if s=="critical" then 5
  elif s=="high" then 4
  elif s=="medium" then 3
  elif s=="low" then 2
  elif s=="nitpick" then 1
  else 0 end;
[.[] | select(rank(._meta.severity) < $min_rank)]')
LOWER_SEVERITY_COUNT=$(echo "$LOWER_SEVERITY" | jq 'length')

if [ "$TOTAL_COUNT" -gt 0 ]; then
  if [ "$LOWER_SEVERITY_COUNT" -gt 0 ]; then
    echo "Found ${TOTAL_COUNT} queued comment(s) (${LOWER_SEVERITY_COUNT} below '${MIN_SEVERITY}' moved to review body)"
  else
    echo "Found ${TOTAL_COUNT} queued inline comment(s)"
  fi
fi

# Build the below-threshold section for the review body (collapsed <details> block)
LOWER_SEVERITY_SECTION=""
if [ "$LOWER_SEVERITY_COUNT" -gt 0 ]; then
  LOWER_SEVERITY_SECTION="<details>
<summary>Lower-severity comments (below ${MIN_SEVERITY}, ${LOWER_SEVERITY_COUNT})</summary>
"

  for i in $(seq 0 $((LOWER_SEVERITY_COUNT - 1))); do
    LOWER_JSON=$(echo "$LOWER_SEVERITY" | jq ".[$i]")
    LS_FILE=$(echo "$LOWER_JSON" | jq -r '._meta.file')
    LS_LINE=$(echo "$LOWER_JSON" | jq -r '._meta.line')
    LS_TITLE=$(echo "$LOWER_JSON" | jq -r '._meta.title // "Untitled"')
    LS_WHY=$(echo "$LOWER_JSON" | jq -r '._meta.why // "No description provided"')
    LS_SUGGESTION=$(echo "$LOWER_JSON" | jq -r 'if ._meta.suggestion == null or ._meta.suggestion == "" then "" else ._meta.suggestion end')
    LS_SEVERITY=$(echo "$LOWER_JSON" | jq -r '._meta.severity // "unknown"')
    LS_SEVERITY_LABEL=$(case "$LS_SEVERITY" in
      critical) echo "🔴 CRITICAL" ;;
      high) echo "🟠 HIGH" ;;
      medium) echo "🟡 MEDIUM" ;;
      low) echo "⚪ LOW" ;;
      nitpick) echo "💬 NITPICK" ;;
      *) echo "$LS_SEVERITY" ;;
    esac)

    LANG=$(ext_to_lang "$LS_FILE")

    # Add separator between entries
    if [ "$i" -gt 0 ]; then
      LOWER_SEVERITY_SECTION="${LOWER_SEVERITY_SECTION}
---
"
    fi

    LOWER_SEVERITY_SECTION="${LOWER_SEVERITY_SECTION}
**${LS_SEVERITY_LABEL}** ${LS_TITLE} — \`${LS_FILE}:${LS_LINE}\`

Why: ${LS_WHY}"

    # Add suggestion as a fenced code block if present
    if [ -n "$LS_SUGGESTION" ]; then
      LOWER_SEVERITY_SECTION="${LOWER_SEVERITY_SECTION}

\`\`\`${LANG}
${LS_SUGGESTION}
\`\`\`"
    fi
  done

  LOWER_SEVERITY_SECTION="${LOWER_SEVERITY_SECTION}

</details>"
fi

# Append standard footer to the review body (if body is provided)
FOOTER='

---
[Why is Claude responding?](https://ela.st/github-ai-tools) | Type `@claude` to interact further

Give us feedback! React with 🚀 if perfect, 👍 if helpful, 👎 if not.'

# Assemble the final review body: user body + nitpick section + footer
FINAL_BODY=""
if [ -n "$BODY" ]; then
  FINAL_BODY="${BODY}"
fi

if [ -n "$LOWER_SEVERITY_SECTION" ]; then
  if [ -n "$FINAL_BODY" ]; then
    FINAL_BODY="${FINAL_BODY}

${LOWER_SEVERITY_SECTION}"
  else
    FINAL_BODY="${LOWER_SEVERITY_SECTION}"
  fi
fi

if [ -n "$FINAL_BODY" ]; then
  BODY_WITH_FOOTER="${FINAL_BODY}${FOOTER}"
else
  BODY_WITH_FOOTER=""
fi

# Build the review request JSON
# Use jq to safely construct the JSON with all special characters handled
REVIEW_JSON=$(jq -n \
  --arg commit_id "$HEAD_SHA" \
  --arg event "$EVENT" \
  --arg body "$BODY_WITH_FOOTER" \
  --argjson comments "$COMMENTS" \
  '{
    commit_id: $commit_id,
    event: $event,
    comments: $comments
  } + (if $body != "" then {body: $body} else {} end)')

# Check if HEAD has changed since review started (race condition detection)
CURRENT_HEAD=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}" --jq '.head.sha')
if [ "$CURRENT_HEAD" != "$HEAD_SHA" ]; then
  echo "⚠️  WARNING: PR head has changed since review started!"
  echo "   Review started at: ${HEAD_SHA:0:7}"
  echo "   Current head:      ${CURRENT_HEAD:0:7}"
  echo ""
  echo "   New commits may have shifted line numbers. Review will be submitted"
  echo "   against the original commit (${HEAD_SHA:0:7}) but comments may be outdated."
  echo ""
fi

echo "Submitting ${EVENT} review for commit ${HEAD_SHA:0:7}..."

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

# Clean up the comments directory after successful submission
if [ -d "${COMMENTS_DIR}" ] && [ "$TOTAL_COUNT" -gt 0 ]; then
  rm -f "${COMMENTS_DIR}"/comment-*.json
  # Remove directory if empty
  rmdir "${COMMENTS_DIR}" 2>/dev/null || true
fi

REVIEW_URL=$(echo "$RESPONSE" | jq -r '.html_url // empty')
REVIEW_STATE=$(echo "$RESPONSE" | jq -r '.state // empty')

if [ -n "$REVIEW_URL" ]; then
  echo "✓ Review submitted (${REVIEW_STATE}): ${REVIEW_URL}"
  if [ "$COMMENT_COUNT" -gt 0 ]; then
    echo "  Included ${COMMENT_COUNT} inline comment(s)"
  fi
  if [ "$LOWER_SEVERITY_COUNT" -gt 0 ]; then
    echo "  Included ${LOWER_SEVERITY_COUNT} below-threshold comment(s) in review body"
  fi
else
  echo "✓ Review submitted successfully"
fi
