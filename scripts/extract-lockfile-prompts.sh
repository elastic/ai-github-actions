#!/usr/bin/env bash
# extract-lockfile-prompts.sh — Extract agent prompt text from compiled .lock.yml files.
#
# Usage: ./scripts/extract-lockfile-prompts.sh [input-dir] [output-dir]
#   input-dir:  directory containing .lock.yml files (default: .github/workflows)
#   output-dir: where to write extracted .prompt.md files (default: /tmp/prompt-audit)
#
# Each lockfile's prompt is assembled from heredoc blocks (our content) and
# cat "/opt/gh-aw/prompts/*.md" runtime includes (platform content). This script
# extracts the heredoc content and marks runtime includes as placeholders.

set -euo pipefail

INPUT_DIR="${1:-.github/workflows}"
OUTPUT_DIR="${2:-/tmp/prompt-audit}"

mkdir -p "$OUTPUT_DIR"

count=0
for lockfile in "$INPUT_DIR"/gh-aw-*.lock.yml; do
  [ -f "$lockfile" ] || continue

  # Derive workflow name from filename: gh-aw-foo-bar.lock.yml → foo-bar
  basename=$(basename "$lockfile")
  name="${basename#gh-aw-}"
  name="${name%.lock.yml}"

  outfile="$OUTPUT_DIR/${name}.prompt.md"

  # State machine to extract prompt content from the "Create prompt" step.
  # States: 0=scanning, 1=in prompt block, 2=in heredoc content
  awk '
    BEGIN { state = 0 }

    # Find the opening brace of the prompt assembly block
    state == 0 && /^[ \t]*\{$/ && saw_create_prompt {
      state = 1
      next
    }

    # Track that we have seen the "Create prompt" step
    /Create prompt with built-in context/ {
      saw_create_prompt = 1
      next
    }

    # End of prompt block
    state >= 1 && /\} > "\$GH_AW_PROMPT"/ {
      exit
    }

    # Runtime file include → placeholder
    state == 1 && /cat "\/opt\/gh-aw\/prompts\// {
      # Extract filename: cat "/opt/gh-aw/prompts/foo.md" → foo.md
      s = $0
      sub(/.*cat "\/opt\/gh-aw\/prompts\//, "", s)
      sub(/".*/, "", s)
      if (s != "") {
        print "<!-- [RUNTIME INCLUDE: " s "] -->"
        print ""
      }
      next
    }

    # Start of heredoc block
    state == 1 && /cat << .GH_AW_PROMPT_EOF./ {
      state = 2
      next
    }

    # End of heredoc block
    state == 2 && /^[ \t]*GH_AW_PROMPT_EOF[ \t]*$/ {
      state = 1
      next
    }

    # Content inside heredoc — strip leading whitespace (lockfile indents with 10 spaces)
    state == 2 {
      sub(/^          /, "")
      print
    }
  ' "$lockfile" > "$outfile"

  # Skip empty extractions (backwards-compat wrapper files, etc.)
  if [ ! -s "$outfile" ]; then
    rm -f "$outfile"
    continue
  fi

  count=$((count + 1))
done

# Write a manifest listing all extracted files with line counts
{
  echo "# Prompt Audit Manifest"
  echo ""
  echo "Extracted prompt text from $count lockfiles in \`$INPUT_DIR/\`."
  echo ""
  echo "| Workflow | Lines | File |"
  echo "| --- | --- | --- |"
  for f in "$OUTPUT_DIR"/*.prompt.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .prompt.md)
    lines=$(wc -l < "$f" | tr -d ' ')
    echo "| $base | $lines | \`$f\` |"
  done
} > "$OUTPUT_DIR/README.md"

echo "Extracted prompts from $count lockfiles → $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"
