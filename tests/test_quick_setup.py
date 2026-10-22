import subprocess
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "quick-setup.sh"


def test_quick_setup_rejects_repo_mismatch(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "origin", "git@github.com:elastic/local.git"],
        check=True,
    )

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text("#!/usr/bin/env bash\nif [ \"$1\" = auth ]; then exit 0; fi\nexit 1\n")
    gh.chmod(0o755)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--repo", "elastic/other"],
        cwd=repo,
        env={"PATH": f"{bin_dir}:{Path('/usr/bin')}", "HOME": str(tmp_path)},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Repository mismatch" in result.stderr
    assert "--allow-repo-mismatch" in result.stderr
