import argparse
import importlib.util
import urllib.error
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "fetch-workflow-logs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fetch_workflow_logs", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_list_workflow_runs_stops_at_since_boundary(monkeypatch):
    module = _load_module()
    calls = []

    def fake_github_api(path, token, accept="application/vnd.github+json"):
        calls.append(path)
        if path.endswith("page=1"):
            return b'{"workflow_runs":[{"id":101,"created_at":"2025-01-03T00:00:00Z","conclusion":"failure"},{"id":100,"created_at":"2025-01-01T00:00:00Z","conclusion":"failure"}]}'
        return b'{"workflow_runs":[{"id":99,"created_at":"2024-12-31T23:59:59Z","conclusion":"failure"}]}'

    monkeypatch.setattr(module, "github_api", fake_github_api)
    runs = module.list_workflow_runs(
        repo="elastic/ai-github-actions",
        workflow="ci.yml",
        token="x",
        since="2025-01-01T00:00:00Z",
        until=None,
        conclusion="failure",
        last=20,
    )

    assert [run["id"] for run in runs] == [101, 100]
    assert len(calls) == 2


def test_list_workflow_runs_stops_at_since_boundary_before_conclusion_filter(monkeypatch):
    module = _load_module()
    calls = []

    def fake_github_api(path, token, accept="application/vnd.github+json"):
        calls.append(path)
        if path.endswith("page=1"):
            return b'{"workflow_runs":[{"id":101,"created_at":"2024-12-31T00:00:00Z","conclusion":"success"}]}'
        return b'{"workflow_runs":[{"id":100,"created_at":"2024-12-30T00:00:00Z","conclusion":"failure"}]}'

    monkeypatch.setattr(module, "github_api", fake_github_api)
    runs = module.list_workflow_runs(
        repo="elastic/ai-github-actions",
        workflow="ci.yml",
        token="x",
        since="2025-01-01T00:00:00Z",
        until=None,
        conclusion="failure",
        last=20,
    )

    assert runs == []
    assert len(calls) == 1


def test_list_workflow_runs_inclusive_date_only_until(monkeypatch):
    module = _load_module()

    def fake_github_api(path, token, accept="application/vnd.github+json"):
        return (
            b'{"workflow_runs":['
            b'{"id":3,"created_at":"2025-01-02T00:00:00Z","conclusion":"failure"},'
            b'{"id":2,"created_at":"2025-01-01T23:59:59Z","conclusion":"failure"},'
            b'{"id":1,"created_at":"2025-01-01T00:00:00Z","conclusion":"failure"}'
            b']}'
            if path.endswith("page=1")
            else b'{"workflow_runs":[]}'
        )

    monkeypatch.setattr(module, "github_api", fake_github_api)
    runs = module.list_workflow_runs(
        repo="elastic/ai-github-actions",
        workflow="ci.yml",
        token="x",
        since=None,
        until="2025-01-01",
        conclusion="failure",
        last=20,
    )

    assert [run["id"] for run in runs] == [2, 1]


def test_conclusion_any_in_fetch_runs(monkeypatch, capsys):
    module = _load_module()

    captured = {}

    def fake_list_workflow_runs(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(module, "list_workflow_runs", fake_list_workflow_runs)
    args = argparse.Namespace(
        workflow="ci.yml",
        repo="elastic/ai-github-actions",
        token="x",
        since=None,
        until=None,
        conclusion="any",
        last=10,
        output_dir="/tmp/gh-aw/agent/logs",
    )

    runs = module._fetch_runs(args)
    stderr = capsys.readouterr().err

    assert runs == []
    assert "Listing runs for ci.yml in elastic/ai-github-actions..." in stderr
    assert captured["conclusion"] is None


def test_github_api_retries_rate_limit_and_honors_retry_after(monkeypatch):
    module = _load_module()
    response = type("Response", (), {
        "__enter__": lambda self: self,
        "__exit__": lambda self, *args: None,
        "read": lambda self: b"ok",
    })()
    calls = [0]

    def fake_urlopen(request, timeout):
        calls[0] += 1
        if calls[0] == 1:
            raise urllib.error.HTTPError("url", 429, "rate limited", {"Retry-After": "0"}, None)
        return response

    sleeps = []
    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(module.time, "sleep", sleeps.append)

    result = module.github_api("/test", "token", retries=1, backoff_seconds=10, timeout=7)

    assert result == b"ok"
    assert result.attempts == 2
    assert sleeps == [0]


def test_download_run_logs_manifest_metadata_on_failure(monkeypatch, tmp_path):
    module = _load_module()
    error = urllib.error.HTTPError("url", 500, "server error", {}, None)
    monkeypatch.setattr(module, "github_api", lambda *args, **kwargs: (_ for _ in ()).throw(error))
    metadata = {}

    files = module.download_run_logs("owner/repo", 123, "token", str(tmp_path),
                                     retries=0, metadata=metadata)

    assert files == []
    assert metadata == {"attempts": 1, "final_error": str(error)}
