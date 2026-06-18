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

# --- Categories ---

DETECTORS=(
  "Trigger Autonomy Atomicity Analyzer"
  "Trigger Breaking Change Detector"
  "Trigger Bug Hunter"
  "Trigger Code Duplication Detector"
  "Trigger Docs Patrol"
  "Trigger Framework Best Practices"
  "Trigger Information Architecture"
  "Trigger Newbie Contributor Patrol"
  "Trigger Prompt Audit"
  "Trigger Stale Issues Investigator"
  "Trigger Test Coverage Detector"
  "Trigger Text Auditor"
  "Trigger UX Design Patrol"
)

FIXERS=(
  "Trigger Refactor Opportunist"
  "Trigger Stale Issues Remediator"
)

MONITORS=(
  "Trigger Agent Suggestions"
  "Trigger Estc Downstream Health"
  "Trigger Product Manager Impersonator"
  "Trigger Project Summary"
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
      echo "Unknown argument: $arg (expected: detectors, fixers, monitors, --dry-run, --list, --help/-h)" >&2
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

# --- Main ---

if [[ "$LIST_ONLY" == "true" ]]; then
  for category in "${CATEGORIES[@]}"; do
    echo "## $(capitalize "$category")"
    get_workflows "$category" | while read -r name; do
      echo "  $name"
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

  get_workflows "$category" | while read -r name; do
    if [[ "$DRY_RUN" == "true" ]]; then
      echo "  [dry-run] $name"
    elif gh workflow run "$name" --repo "$REPO" --ref "$REF" 2>/dev/null; then
      echo "  ✓ $name"
    else
      echo "  ✗ $name (dispatch failed)" >&2
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
