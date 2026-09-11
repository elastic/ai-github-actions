import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "extract_lockfile_prompts.py"
)
CURRENT_LOCKFILE = (
    Path(__file__).resolve().parent.parent
    / ".github"
    / "workflows"
    / "gh-aw-framework-best-practices.lock.yml"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("extract_lockfile_prompts", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_script(input_dir: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(input_dir), str(output_dir)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_extract_prompts_from_run_supports_legacy_markers():
    module = _load_module()
    run_script = """
{
cat "/opt/gh-aw/prompts/base.md"
cat << 'GH_AW_PROMPT_EOF'
hello
world
GH_AW_PROMPT_EOF
} > "$GH_AW_PROMPT"
""".strip()

    extracted = module.extract_prompts_from_run(run_script)

    assert "<!-- [RUNTIME INCLUDE: base.md] -->" in extracted
    assert "hello" in extracted
    assert "world" in extracted


def test_cli_extracts_current_lockfile_prompt_block(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    lockfile_copy = input_dir / CURRENT_LOCKFILE.name
    lockfile_copy.write_text(CURRENT_LOCKFILE.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run_script(input_dir, output_dir)

    assert result.returncode == 0
    extracted_file = output_dir / "framework-best-practices.prompt.md"
    assert extracted_file.exists()

    extracted = extracted_file.read_text(encoding="utf-8")
    assert "<!-- [RUNTIME INCLUDE: xpia.md] -->" in extracted
    assert "<safe-output-tools>" in extracted
    assert "</system>" in extracted

    manifest = (output_dir / "README.md").read_text(encoding="utf-8")
    assert "Extracted prompt text from 1 lockfiles" in manifest
    assert "framework-best-practices" in manifest


def test_cli_skips_lockfile_without_create_prompt_step(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    lockfile_data = {
        "jobs": {
            "run": {
                "steps": [
                    {"name": "Checkout", "run": "echo hi"},
                ]
            }
        }
    }
    (input_dir / "gh-aw-empty.lock.yml").write_text(
        yaml.safe_dump(lockfile_data), encoding="utf-8"
    )

    result = _run_script(input_dir, output_dir)

    assert result.returncode == 0
    assert not (output_dir / "empty.prompt.md").exists()
    manifest = (output_dir / "README.md").read_text(encoding="utf-8")
    assert "Extracted prompt text from 0 lockfiles" in manifest
