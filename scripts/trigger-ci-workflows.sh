#!/usr/bin/env bash
# Trigger continuous-improvement workflows via workflow_dispatch.
#
# Usage:
#   ./scripts/trigger-ci-workflows.sh                    # trigger all categories
#   ./scripts/trigger-ci-workflows.sh detectors           # trigger one category
#   ./scripts/trigger-ci-workflows.sh fixers monitors     # trigger multiple categories
#   ./scripts/trigger-ci-workflows.sh --dry-run           # show what would be triggered
#   ./scripts/trigger-ci-workflows.sh --list              # list workflows by category

set -euo pipefail

REPO="elastic/ai-github-actions"
REF="main"
WORKFLOWS_DIR=".github/workflows"

# --- Categories ---

DETECTORS=(
  "trigger-autonomy-atomicity-analyzer.yml"
  "trigger-breaking-change-detector.yml"
  "trigger-bug-hunter.yml"
  "trigger-code-duplication-detector.yml"
  "trigger-docs-patrol.yml"
  "trigger-framework-best-practices.yml"
  "trigger-information-architecture.yml"
  "trigger-newbie-contributor-patrol.yml"
  "trigger-prompt-audit.yml"
  "trigger-stale-issues-investigator.yml"
  "trigger-test-coverage-detector.yml"
  "trigger-text-auditor.yml"
  "trigger-ux-design-patrol.yml"
)

FIXERS=(
  "trigger-refactor-opportunist.yml"
  "trigger-stale-issues-remediator.yml"
)

MONITORS=(
  "trigger-agent-suggestions.yml"
  "trigger-internal-downstream-health.yml"
  "trigger-product-manager-impersonator.yml"
  "trigger-project-summary.yml"
)

ALL_CATEGORIES=(detectors fixers monitors)

# --- Argument parsing ---

DRY_RUN=false
LIST_ONLY=false
CATEGORIES=()

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --list)    LIST_ONLY=true ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--list] [category ...]"
      echo ""
      echo "Categories: detectors, fixers, monitors"
      echo "  detectors  — find issues, drift, stale items, breaking changes"
      echo "  fixers     — refactor code, remediate stale issues"
      echo "  monitors   — downstream health, project summaries, suggestions"
      echo ""
      echo "  --dry-run  Show what would be triggered without dispatching"
      echo "  --list     List workflows by category"
      echo ""
      echo "If no categories are specified, all are triggered."
      exit 0
      ;;
    detectors|fixers|monitors)
      CATEGORIES+=("$arg")
      ;;
    *)
      echo "Unknown argument: $arg (expected: detectors, fixers, monitors, --dry-run, --list, --help)" >&2
      exit 1
      ;;
  esac
done

if [[ ${#CATEGORIES[@]} -eq 0 ]]; then
  CATEGORIES=("${ALL_CATEGORIES[@]}")
fi

# --- Helpers ---

get_workflows() {
  local category="$1"
  case "$category" in
    detectors) printf '%s\n' "${DETECTORS[@]}" ;;
    fixers)    printf '%s\n' "${FIXERS[@]}" ;;
    monitors)  printf '%s\n' "${MONITORS[@]}" ;;
  esac
}

capitalize() {
  echo "$1" | awk '{print toupper(substr($0,1,1)) substr($0,2)}'
}

validate_workflow_target() {
  local workflow_file="$1"
  if [[ ! -f "$WORKFLOWS_DIR/$workflow_file" ]]; then
    echo "  ✗ missing workflow file: $WORKFLOWS_DIR/$workflow_file" >&2
    return 1
  fi
}

# --- Main ---

if [[ "$LIST_ONLY" == "true" ]]; then
  for category in "${CATEGORIES[@]}"; do
    echo "## $(capitalize "$category")"
    get_workflows "$category" | while read -r workflow_file; do
      echo "  $workflow_file"
    done
    echo ""
  done
  exit 0
fi

total=0
succeeded=0
failed=0

for category in "${CATEGORIES[@]}"; do
  echo "## $(capitalize "$category")"
  echo ""

  get_workflows "$category" | while read -r workflow_file; do
    if ! validate_workflow_target "$workflow_file"; then
      exit 1
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
      echo "  [dry-run] $workflow_file"
    elif gh workflow run "$workflow_file" --repo "$REPO" --ref "$REF" 2>/dev/null; then
      echo "  ✓ $workflow_file"
    else
      echo "  ✗ $workflow_file (dispatch failed)" >&2
    fi
  done

  echo ""
done

if [[ "$DRY_RUN" == "false" ]]; then
  # Re-count for summary (subshell above doesn't propagate counts)
  for category in "${CATEGORIES[@]}"; do
    case "$category" in
      detectors) total=$((total + ${#DETECTORS[@]})) ;;
      fixers)    total=$((total + ${#FIXERS[@]})) ;;
      monitors)  total=$((total + ${#MONITORS[@]})) ;;
    esac
  done
  echo "Attempted to dispatch $total workflows across ${#CATEGORIES[@]} categories."
fi
