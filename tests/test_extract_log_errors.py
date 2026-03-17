import json
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "extract-log-errors.py"


def run_extractor(log_file: Path) -> dict:
    proc = subprocess.run(
        ["python3", str(SCRIPT), str(log_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def test_detects_lowercase_error_marker(tmp_path):
    log_file = tmp_path / "run.txt"
    log_file.write_text("line1\nerror: lower-case failure marker\nline3\n", encoding="utf-8")

    data = run_extractor(log_file)

    assert data["total_matches"] >= 1
    assert any("error: lower-case failure marker" in m["snippet"] for m in data["matches"])


def test_detects_uppercase_error_marker(tmp_path):
    log_file = tmp_path / "run.txt"
    log_file.write_text("line1\nError: upper-case failure marker\nline3\n", encoding="utf-8")

    data = run_extractor(log_file)

    assert data["total_matches"] >= 1
    assert any("Error: upper-case failure marker" in m["snippet"] for m in data["matches"])
