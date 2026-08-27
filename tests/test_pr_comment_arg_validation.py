import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
PR_COMMENT = ROOT / "claude-workflows" / "pr-review" / "scripts" / "pr-comment.sh"


def run_pr_comment(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PR_REVIEW_REPO"] = "elastic/ai-github-actions"
    env["PR_REVIEW_PR_NUMBER"] = "1"
    return subprocess.run(
        ["bash", str(PR_COMMENT), *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("args", "expected_message"),
    [
        (("README.md", "1", "--severity"), "Missing value for --severity"),
        (
            ("README.md", "1", "--severity", "high", "--title"),
            "Missing value for --title",
        ),
        (
            ("README.md", "1", "--severity", "high", "--title", "desc", "--why"),
            "Missing value for --why",
        ),
        (
            (
                "README.md",
                "1",
                "--severity",
                "--title",
                "desc",
                "--why",
                "impact",
                "--no-suggestion",
            ),
            "Missing value for --severity",
        ),
    ],
)
def test_missing_named_argument_values_emit_actionable_errors(args, expected_message):
    result = run_pr_comment(*args)

    assert result.returncode != 0
    assert "Error:" in result.stderr
    assert expected_message in result.stderr
