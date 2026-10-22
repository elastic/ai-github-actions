import os
import stat
import subprocess
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "claude-workflows" / "pr-review" / "scripts" / "pr-prior-reviews.sh"


def _write_stub_gh(tmp_path: Path, body: str) -> Path:
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    gh_path = stub_dir / "gh"
    gh_path.write_text(body)
    gh_path.chmod(gh_path.stat().st_mode | stat.S_IEXEC)
    return stub_dir


def _run_script(path_prefix: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{path_prefix}:{env['PATH']}"
    env["PR_REVIEW_REPO"] = "elastic/ai-github-actions"
    env["PR_REVIEW_PR_NUMBER"] = "1"
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


def test_exits_nonzero_when_gh_api_fails(tmp_path: Path):
    stub_dir = _write_stub_gh(
        tmp_path,
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            echo "simulated gh failure" >&2
            exit 1
            """
        ),
    )

    result = _run_script(stub_dir)
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0
    assert "Failed to fetch prior PR reviews." in combined_output
    assert "No prior reviews with body text found." not in combined_output


def test_prints_empty_message_when_no_review_bodies(tmp_path: Path):
    stub_dir = _write_stub_gh(
        tmp_path,
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            printf '[]'
            """
        ),
    )

    result = _run_script(stub_dir)

    assert result.returncode == 0
    assert "No prior reviews with body text found." in result.stdout
