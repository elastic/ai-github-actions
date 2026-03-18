import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "fetch-workflow-logs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fetch_workflow_logs", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_zip(file_map: dict[str, bytes] | None = None) -> bytes:
    file_map = file_map or {}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in file_map.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_download_run_logs_invalid_zip_warns_and_returns_empty(tmp_path, monkeypatch, capsys):
    module = _load_module()
    run_id = 123

    monkeypatch.setattr(module, "github_api", lambda *args, **kwargs: b"not-a-zip")
    saved = module.download_run_logs("elastic/ai-github-actions", run_id, "token", str(tmp_path))

    assert saved == []
    err = capsys.readouterr().err
    assert f"could not parse logs zip for run {run_id}" in err


def test_download_run_logs_non_txt_entries_returns_empty_without_warning(tmp_path, monkeypatch, capsys):
    module = _load_module()

    monkeypatch.setattr(
        module,
        "github_api",
        lambda *args, **kwargs: _build_zip({"job/step.log": b"log", "artifact.json": b"{}"}),
    )
    saved = module.download_run_logs("elastic/ai-github-actions", 456, "token", str(tmp_path))

    assert saved == []
    assert capsys.readouterr().err == ""


def test_main_continues_after_bad_zip_and_writes_partial_manifest(tmp_path, monkeypatch, capsys):
    module = _load_module()
    bad_run_id = 1001
    good_run_id = 1002

    runs = [
        {"id": bad_run_id, "created_at": "2026-03-01T00:00:00Z", "conclusion": "failure", "html_url": "bad"},
        {"id": good_run_id, "created_at": "2026-03-02T00:00:00Z", "conclusion": "failure", "html_url": "good"},
    ]
    monkeypatch.setattr(module, "list_workflow_runs", lambda **kwargs: runs)

    valid_zip = _build_zip({"job/1_step.txt": b"ok log"})

    def fake_github_api(path, token, accept="application/vnd.github+json"):
        if path.endswith(f"/runs/{bad_run_id}/logs"):
            return b"not-a-zip"
        if path.endswith(f"/runs/{good_run_id}/logs"):
            return valid_zip
        raise AssertionError(f"Unexpected API path: {path}")

    monkeypatch.setattr(module, "github_api", fake_github_api)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "fetch-workflow-logs.py",
            "trigger-pr-review.yml",
            "--repo",
            "elastic/ai-github-actions",
            "--token",
            "token",
            "--output-dir",
            str(tmp_path),
            "--last",
            "2",
        ],
    )

    module.main()

    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert len(manifest) == 2
    assert manifest[0]["run_id"] == bad_run_id
    assert manifest[0]["log_files"] == []
    assert manifest[1]["run_id"] == good_run_id
    assert len(manifest[1]["log_files"]) == 1
    assert Path(manifest[1]["log_files"][0]).read_bytes() == b"ok log"

    err = capsys.readouterr().err
    assert f"could not parse logs zip for run {bad_run_id}" in err
