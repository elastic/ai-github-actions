import argparse
import importlib.util
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
