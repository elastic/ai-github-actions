"""Regression tests for PR review RO helper script allowlist patterns."""
from pathlib import Path

import yaml


ACTION_PATH = (
    Path(__file__).resolve().parent.parent
    / "claude-workflows"
    / "pr-review"
    / "ro"
    / "action.yml"
)


def _allowed_tools_default() -> str:
    action = yaml.safe_load(ACTION_PATH.read_text())
    return action["inputs"]["allowed-tools"]["default"]


def test_pr_review_ro_uses_pinned_actions_path_patterns_for_helpers():
    allowed_tools = _allowed_tools_default()

    expected_patterns = [
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/claude-workflows/pr-review/scripts/pr-comment.sh:*)",
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/claude-workflows/pr-review/scripts/pr-remove-comment.sh:*)",
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/claude-workflows/pr-review/scripts/pr-review.sh:*)",
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/claude-workflows/pr-review/scripts/pr-diff.sh:*)",
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/claude-workflows/pr-review/scripts/pr-existing-comments.sh:*)",
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/claude-workflows/pr-review/scripts/pr-prior-reviews.sh:*)",
    ]

    for pattern in expected_patterns:
        assert pattern in allowed_tools


def test_pr_review_ro_does_not_use_literal_github_action_path_for_helpers():
    allowed_tools = _allowed_tools_default()
    assert "${{ github.action_path }}/../scripts/pr-comment.sh:*" not in allowed_tools


def test_pr_review_ro_helper_patterns_are_not_broad_wildcards():
    allowed_tools = _allowed_tools_default()

    assert "Bash(*/claude-workflows/pr-review/scripts/pr-comment.sh:*)" not in allowed_tools
    assert (
        "Bash(/home/runner/work/_actions/elastic/ai-github-actions/*/"
        "claude-workflows/pr-review/scripts/pr-comment.sh:*)"
    ) in allowed_tools
