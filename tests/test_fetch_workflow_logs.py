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


class _FakeResponse:
    def __init__(self, payload, *, links=None, content=b""):
        self._payload = payload
        self.links = links or {}
        self.content = content

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}
        self.closed = False

    def get(self, url, params=None, timeout=None):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
        })
        return self.responses.pop(0)

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


def test_github_api_sets_auth_header_and_timeout(monkeypatch):
    module = _load_module()
    fake_session = _FakeSession([_FakeResponse(payload={})])
    monkeypatch.setattr(module.requests, "Session", lambda: fake_session)

    module.github_api(
        "/repos/elastic/ai-github-actions/actions/workflows/ci.yml/runs",
        token="secret-token",
    )

    assert fake_session.headers["Authorization"] == "Bearer secret-token"
    assert fake_session.headers["Accept"] == "application/vnd.github+json"
    assert fake_session.headers["X-GitHub-Api-Version"] == "2022-11-28"
    assert fake_session.calls[0]["timeout"] == module.DEFAULT_TIMEOUT_SECONDS


def test_iter_workflow_run_pages_follows_next_link(monkeypatch):
    module = _load_module()
    responses = [
        _FakeResponse(
            payload={"workflow_runs": [{"id": 101}]},
            links={"next": {"url": "https://api.github.com/next-page"}},
        ),
        _FakeResponse(payload={"workflow_runs": [{"id": 100}]}, links={}),
    ]
    fake_session = _FakeSession(responses)
    monkeypatch.setattr(module, "_github_session", lambda token: fake_session)

    pages = list(module._iter_workflow_run_pages(
        repo="elastic/ai-github-actions",
        workflow="ci.yml",
        token="x",
    ))

    assert pages == [[{"id": 101}], [{"id": 100}]]
    assert fake_session.calls[0]["params"] == {"per_page": 100}
    assert fake_session.calls[1]["params"] is None


def test_list_workflow_runs_stops_at_since_boundary(monkeypatch):
    module = _load_module()

    monkeypatch.setattr(module, "_iter_workflow_run_pages", lambda **kwargs: iter([
        [
            {"id": 101, "created_at": "2025-01-03T00:00:00Z", "conclusion": "failure"},
            {"id": 100, "created_at": "2025-01-01T00:00:00Z", "conclusion": "failure"},
        ],
        [{"id": 99, "created_at": "2024-12-31T23:59:59Z", "conclusion": "failure"}],
    ]))

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


def test_list_workflow_runs_stops_at_since_boundary_before_conclusion_filter(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_iter_workflow_run_pages", lambda **kwargs: iter([
        [{"id": 101, "created_at": "2024-12-31T00:00:00Z", "conclusion": "success"}],
        [{"id": 100, "created_at": "2024-12-30T00:00:00Z", "conclusion": "failure"}],
    ]))

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


def test_list_workflow_runs_inclusive_date_only_until(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_iter_workflow_run_pages", lambda **kwargs: iter([
        [
            {"id": 3, "created_at": "2025-01-02T00:00:00Z", "conclusion": "failure"},
            {"id": 2, "created_at": "2025-01-01T23:59:59Z", "conclusion": "failure"},
            {"id": 1, "created_at": "2025-01-01T00:00:00Z", "conclusion": "failure"},
        ]
    ]))

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
