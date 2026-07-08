import os
import stat
import subprocess
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "claude-workflows"
    / "pr-review"
    / "scripts"
    / "pr-review.sh"
)


def test_skips_duplicate_review_when_paginated_last_state_matches(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gh_calls = tmp_path / "gh-calls.log"

    fake_gh = fake_bin / "gh"
    fake_gh.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "echo \"$*\" >> \"$GH_CALLS_LOG\"\n"
        "if [[ \"$*\" == *\"repos/elastic/ai-github-actions/pulls/123/reviews\"* ]] && [[ \"$*\" == *\"--paginate\"* ]]; then\n"
        "  printf '%s\\n' "
        "'[{\"user\":{\"login\":\"copilot\"},\"state\":\"COMMENTED\"}]' "
        "'[{\"user\":{\"login\":\"copilot\"},\"state\":\"APPROVED\"}]'\n"
        "  exit 0\n"
        "fi\n"
        "echo \"unexpected gh invocation: $*\" >&2\n"
        "exit 1\n"
    )
    fake_gh.chmod(fake_gh.stat().st_mode | stat.S_IEXEC)

    env = os.environ.copy()
    env.update(
        {
            "PR_REVIEW_REPO": "elastic/ai-github-actions",
            "PR_REVIEW_PR_NUMBER": "123",
            "PR_REVIEW_HEAD_SHA": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "PR_REVIEW_BOT_LOGIN": "copilot",
            "PR_REVIEW_COMMENTS_DIR": str(tmp_path / "comments"),
            "GH_CALLS_LOG": str(gh_calls),
            "PATH": f"{fake_bin}:{env['PATH']}",
        }
    )

    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "APPROVE"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "Skipping review — no new comments and verdict unchanged" in result.stdout
    calls = gh_calls.read_text().splitlines()
    assert calls == ["api repos/elastic/ai-github-actions/pulls/123/reviews --paginate"]
