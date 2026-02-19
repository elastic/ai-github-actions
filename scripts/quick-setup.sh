#!/usr/bin/env bash
# Quick setup for GitHub Agent Workflows in a repository.
#
# Usage:
#   ./scripts/quick-setup.sh [--repo OWNER/REPO] [--branch NAME]
#                            [--workflows "pr-review,issue-triage,..."]
#                            [--skip-secret] [--dry-run]

set -euo pipefail

branch="ai-gh-aw-setup"
repo=""
workflows_csv=""
skip_secret=false
dry_run=false

usage() {
  cat <<'EOF'
Usage: quick-setup.sh [options]

Options:
  --repo OWNER/REPO     Repository to configure (defaults to current repo)
  --branch NAME         Branch name to create (default: ai-gh-aw-setup)
  --workflows CSV       Comma-separated workflow list (default: recommended set)
  --skip-secret         Skip setting COPILOT_GITHUB_TOKEN
  --dry-run             Print actions without making changes
  -h, --help            Show this help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      repo="${2:-}"
      shift 2
      ;;
    --branch)
      branch="${2:-}"
      shift 2
      ;;
    --workflows)
      workflows_csv="${2:-}"
      shift 2
      ;;
    --skip-secret)
      skip_secret=true
      shift
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown flag: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd gh
require_cmd git
require_cmd curl

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree has uncommitted changes. Commit or stash before running." >&2
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "GitHub CLI not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

if [ -z "$repo" ]; then
  repo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
fi

if [ -z "$repo" ]; then
  echo "Unable to determine repository. Use --repo OWNER/REPO." >&2
  exit 1
fi

if [ -z "$branch" ]; then
  echo "Branch name cannot be empty." >&2
  exit 1
fi

base_url="https://raw.githubusercontent.com/elastic/ai-github-actions/v0"
default_workflows=(
  pr-review
  issue-triage
  mention-in-issue
  mention-in-pr
  pr-ci-detective
  pr-ci-fixer
)

if [ -n "$workflows_csv" ]; then
  workflows_csv="${workflows_csv// /}"
  IFS=',' read -r -a workflows <<< "$workflows_csv"
else
  workflows=("${default_workflows[@]}")
fi

workflow_dir=".github/workflows"
created_files=()

if [ "$dry_run" = true ]; then
  echo "dry-run: mkdir -p $workflow_dir"
else
  mkdir -p "$workflow_dir"
fi

for workflow in "${workflows[@]}"; do
  [ -n "$workflow" ] || continue
  src="$base_url/gh-agent-workflows/$workflow/example.yml"
  dest="$workflow_dir/trigger-$workflow.yml"
  if [ "$dry_run" = true ]; then
    echo "dry-run: curl -fsSL $src -o $dest"
  else
    curl -fsSL "$src" -o "$dest"
    created_files+=("$dest")
  fi
done

maintenance_src="$base_url/.github/workflows/agentics-maintenance.yml"
maintenance_dest="$workflow_dir/agentics-maintenance.yml"
if [ "$dry_run" = true ]; then
  echo "dry-run: curl -fsSL $maintenance_src -o $maintenance_dest"
else
  curl -fsSL "$maintenance_src" -o "$maintenance_dest"
  created_files+=("$maintenance_dest")
fi

if [ "$skip_secret" = false ]; then
  token="${COPILOT_GITHUB_TOKEN:-}"
  if [ -z "$token" ] && [ "$dry_run" = false ]; then
    read -r -s -p "Enter Copilot PAT (copilot-requests scope): " token
    echo
  fi
  if [ -z "$token" ] && [ "$dry_run" = false ]; then
    echo "COPILOT_GITHUB_TOKEN is required (set env var or enter at prompt)." >&2
    exit 1
  fi
  if [ "$dry_run" = true ]; then
    echo "dry-run: gh secret set COPILOT_GITHUB_TOKEN --repo $repo --body-file -"
  else
    printf '%s' "$token" | gh secret set COPILOT_GITHUB_TOKEN --repo "$repo" --body-file -
  fi
  unset token
fi

if [ "$dry_run" = true ]; then
  echo "dry-run: git checkout -b $branch"
else
  if git show-ref --verify --quiet "refs/heads/$branch"; then
    git checkout "$branch"
  else
    git checkout -b "$branch"
  fi
fi

if [ "$dry_run" = true ]; then
  echo "dry-run: git add ${created_files[*]}"
  echo "dry-run: git commit -m \"Add gh-aw workflows\""
  echo "dry-run: git push -u origin $branch"
  echo "dry-run: gh pr create --repo $repo --fill"
  exit 0
fi

git add "${created_files[@]}"

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "Add gh-aw workflows"
git push -u origin "$branch"
gh pr create --repo "$repo" --fill

echo "Installed workflows: ${workflows[*]}"
