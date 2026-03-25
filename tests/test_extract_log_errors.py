import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "extract-log-errors.py"
)


def load_script_module():
    spec = importlib.util.spec_from_file_location("extract_log_errors", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_extract_matches_coalesces_context_blocks(tmp_path):
    script = load_script_module()
    log_file = tmp_path / "sample.log"
    log_file.write_text(
        "\n".join(
            [
                "line 1",
                "line 2 error",
                "line 3",
                "line 4 error",
                "line 5",
            ]
        )
        + "\n"
    )

    matches = script.extract_matches(
        str(log_file), [script.re.compile(r"\berror\b")], context=1
    )

    assert len(matches) == 1
    assert matches[0]["start_line"] == 1
    assert matches[0]["end_line"] == 5
    assert "line 2 error" in matches[0]["snippet"]
    assert "line 4 error" in matches[0]["snippet"]


def test_main_manifest_attaches_run_metadata(tmp_path):
    logs_root = tmp_path / "logs"
    run_one = logs_root / "1001"
    run_two = logs_root / "1002"
    run_one.mkdir(parents=True)
    run_two.mkdir(parents=True)

    log_one = run_one / "job1.txt"
    log_two = run_two / "job2.txt"
    log_one.write_text("prep\n##[error] failure in step\n")
    log_two.write_text("info\nThe process 'x' failed\n")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "run_id": 1001,
                    "conclusion": "failure",
                    "created_at": "2026-03-17T00:00:00Z",
                    "html_url": "https://example.invalid/run/1001",
                    "log_files": [str(log_one)],
                },
                {
                    "run_id": 1002,
                    "conclusion": "failure",
                    "created_at": "2026-03-17T00:01:00Z",
                    "html_url": "https://example.invalid/run/1002",
                    "log_files": [str(log_two)],
                },
            ]
        )
    )

    output_path = tmp_path / "result.json"
    result = run_script("--manifest", str(manifest), "--output", str(output_path), "--context", "0")

    assert result.returncode == 0
    summary = json.loads(output_path.read_text())
    assert summary["total_files_scanned"] == 2
    assert summary["total_matches"] == 2
    run_ids = {match["run"]["run_id"] for match in summary["matches"]}
    assert run_ids == {1001, 1002}


def test_default_patterns_match_lowercase_error(tmp_path):
    script = load_script_module()
    log_file = tmp_path / "lower.log"
    log_file.write_text("line1\nerror: lower-case failure marker\nline3\n")

    patterns = [script.re.compile(p) for p in script.DEFAULT_PATTERNS]
    matches = script.extract_matches(str(log_file), patterns, context=0)

    assert len(matches) == 1
    assert "error: lower-case failure marker" in matches[0]["snippet"]


def test_main_writes_empty_output_for_empty_manifest_logs(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "run_id": 2001,
                    "conclusion": "success",
                    "created_at": "2026-03-17T00:00:00Z",
                    "html_url": "https://example.invalid/run/2001",
                    "log_files": [],
                }
            ]
        )
    )

    output_path = tmp_path / "empty.json"
    result = run_script("--manifest", str(manifest), "--output", str(output_path))

    assert result.returncode == 0
    assert output_path.exists()
    assert json.loads(output_path.read_text()) == {
        "total_files_scanned": 0,
        "total_matches": 0,
        "matches": [],
        "file_errors": [],
    }


def test_main_manifest_separates_missing_file_errors_from_matches(tmp_path):
    manifest = tmp_path / "manifest.json"
    missing_file = tmp_path / "does-not-exist.txt"
    manifest.write_text(
        json.dumps(
            [
                {
                    "run_id": 3001,
                    "conclusion": "failure",
                    "created_at": "2026-03-25T00:00:00Z",
                    "html_url": "https://example.invalid/run/3001",
                    "log_files": [str(missing_file)],
                }
            ]
        )
    )

    output_path = tmp_path / "result.json"
    result = run_script("--manifest", str(manifest), "--output", str(output_path), "--context", "0")

    assert result.returncode == 0
    summary = json.loads(output_path.read_text())
    assert summary["total_files_scanned"] == 1
    assert summary["total_matches"] == 0
    assert summary["matches"] == []
    assert summary["file_errors"] == [
        {
            "file": str(missing_file),
            "error": "File not found",
            "run": {
                "run_id": 3001,
                "conclusion": "failure",
                "created_at": "2026-03-25T00:00:00Z",
                "html_url": "https://example.invalid/run/3001",
            },
        }
    ]
