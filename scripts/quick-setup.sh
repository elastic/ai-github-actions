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
continuous_improvement=false
dry_run=false

usage() {
  cat <<'EOF'
Usage: quick-setup.sh [options]

Options:
  --repo OWNER/REPO     Repository to configure (defaults to current repo)
  --branch NAME         Branch name to create (default: ai-gh-aw-setup)
  --workflows CSV       Comma-separated workflow list (default: recommended set)
  --skip-secret         Skip setting COPILOT_GITHUB_TOKEN
  --continuous-improvement
                        Add recommended continuous improvement workflows
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
    --continuous-improvement)
      continuous_improvement=true
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

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$repo_root" ]; then
  echo "Run this script from inside a git repository." >&2
  exit 1
fi
cd "$repo_root"

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree has uncommitted changes. Commit or stash before running." >&2
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

if [ -z "$repo" ]; then
  repo="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
fi

if [ -z "$repo" ]; then
  echo "Unable to determine repository. Use --repo OWNER/REPO." >&2
  exit 1
fi

if [ -z "$branch" ]; then
  echo "Branch name cannot be empty." >&2
  exit 1
fi

default_branch="$(gh repo view "$repo" --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || true)"
if [ -z "$default_branch" ]; then
  echo "Unable to determine default branch for $repo." >&2
  exit 1
fi

base_url="https://raw.githubusercontent.com/elastic/ai-github-actions/v0"
default_workflows=(
  pr-review
  issue-triage
  mention-in-issue
  mention-in-pr
  pr-actions-detective
)
continuous_improvement_workflows=(
  bug-hunter
  bug-exterminator
  code-simplifier
  docs-patrol
  newbie-contributor-patrol
  product-manager-impersonator
  refactor-opportunist
  small-problem-fixer
  stale-issues
  test-improver
  breaking-change-detector
  code-duplication-detector
  update-pr-body
)

if [ -n "$workflows_csv" ]; then
  workflows_csv="${workflows_csv// /}"
  IFS=',' read -r -a workflows <<<"$workflows_csv"
else
  workflows=("${default_workflows[@]}")
fi

append_workflow_if_missing() {
  local candidate="$1"
  local existing
  for existing in "${workflows[@]}"; do
    if [ "$existing" = "$candidate" ]; then
      return
    fi
  done
  workflows+=("$candidate")
}

if [ "$continuous_improvement" = true ]; then
  for workflow in "${continuous_improvement_workflows[@]}"; do
    append_workflow_if_missing "$workflow"
  done
fi

if [ "${#workflows[@]}" -eq 0 ]; then
  echo "Workflow list cannot be empty." >&2
  exit 1
fi

if [ "$dry_run" = true ]; then
  echo "dry-run: git fetch origin $default_branch"
  echo "dry-run: git checkout -b $branch origin/$default_branch"
else
  git fetch --quiet origin "$default_branch"
  if git show-ref --verify --quiet "refs/heads/$branch"; then
    git checkout "$branch"
  else
    git checkout -b "$branch" "origin/$default_branch"
  fi
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
  if [ -z "$token" ]; then
    token_url="https://github.com/settings/personal-access-tokens/new?name=COPILOT_GITHUB_TOKEN+for+${repo//\//%2F}&description=Copilot+requests+for+GitHub+Agent+Workflows&copilot_requests=write"
    if [ "$dry_run" = true ]; then
      echo "dry-run: open $token_url"
      echo "dry-run: prompt for token"
      echo "dry-run: printf '%s' \"(token)\" | gh secret set COPILOT_GITHUB_TOKEN --repo $repo"
    elif [ -t 0 ]; then
      echo "A fine-grained PAT with the 'Copilot requests' permission is needed."
      echo "Opening browser to create one..."
      if command -v open >/dev/null 2>&1; then
        open "$token_url"
      elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$token_url"
      else
        echo "Visit: $token_url"
      fi
      printf "Paste the token here: "
      read -r -s token
      echo
      if [ -z "$token" ]; then
        echo "No token provided. Use --skip-secret to set it manually later." >&2
        exit 1
      fi
    else
      echo "No COPILOT_GITHUB_TOKEN set and stdin is not a terminal." >&2
      echo "Set COPILOT_GITHUB_TOKEN in your environment, or use --skip-secret." >&2
      exit 1
    fi
  fi

  if [ "$dry_run" != true ]; then
    printf '%s' "$token" | gh secret set COPILOT_GITHUB_TOKEN --repo "$repo"
  fi
  unset token
fi

if [ "$dry_run" = true ]; then
  echo "dry-run: git add .github/workflows/trigger-*.yml .github/workflows/agentics-maintenance.yml"
  echo "dry-run: git commit -m \"Add gh-aw workflows via quick setup\""
  echo "dry-run: git push -u origin $branch"
  echo "dry-run: gh pr create --repo $repo --fill"
  exit 0
fi

git add "${created_files[@]}"

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "Add gh-aw workflows via quick setup"
git push -u origin "$branch"
gh pr create --repo "$repo" --fill

echo "Installed workflows: ${workflows[*]}"
