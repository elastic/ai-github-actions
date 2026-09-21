import os
import stat
import subprocess
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "trigger-ci-workflows.sh"
)


def test_returns_non_zero_when_workflow_dispatch_fails(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    gh_stub = bin_dir / "gh"
    gh_stub.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == \"workflow\" && \"$2\" == \"run\" ]]; then\n"
        "  exit 1\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    gh_stub.chmod(gh_stub.stat().st_mode | stat.S_IEXEC)

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "detectors"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 1
    assert "dispatch failed" in result.stderr
    assert "0 succeeded, 13 failed" in result.stdout
