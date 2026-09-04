import json
import os
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PR_EXISTING_COMMENTS = ROOT / "claude-workflows" / "pr-review" / "scripts" / "pr-existing-comments.sh"
GET_REVIEW_THREADS = ROOT / "claude-workflows" / "mention-in-pr" / "scripts" / "gh-get-review-threads.sh"


def _write_gh_stub(tmp_path: Path) -> Path:
    stub = tmp_path / "gh"
    stub.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            import sys

            def parse_fields(argv):
                fields = {}
                idx = 0
                while idx < len(argv):
                    token = argv[idx]
                    if token in ("-F", "-f") and idx + 1 < len(argv):
                        value = argv[idx + 1]
                        if "=" in value:
                            key, val = value.split("=", 1)
                            fields[key] = val
                        idx += 2
                        continue
                    idx += 1
                return fields

            def make_comment(number, include_commit):
                comment = {
                    "id": f"comment-{number}",
                    "body": f"Comment {number}",
                    "author": {"login": "reviewer"},
                    "createdAt": "2026-01-01T00:00:00Z",
                }
                if include_commit:
                    comment["originalCommit"] = {"abbreviatedOid": "abc1234"}
                return comment

            fields = parse_fields(sys.argv[1:])
            query = fields.get("query", "")
            threads_after = fields.get("threadsAfter", "")
            comments_after = fields.get("commentsAfter", "")
            include_commit = "originalCommit" in query

            if "reviewThreads(first: 100" in query:
                if not threads_after:
                    comments = [make_comment(i, include_commit) for i in range(1, 51)]
                    response = {
                        "data": {
                            "repository": {
                                "pullRequest": {
                                    "reviewThreads": {
                                        "pageInfo": {"hasNextPage": True, "endCursor": "threads-cursor-1"},
                                        "nodes": [
                                            {
                                                "id": "thread-1",
                                                "isResolved": False,
                                                "isOutdated": False,
                                                "path": "src/example.py",
                                                "line": 10,
                                                "originalLine": 10,
                                                "startLine": None,
                                                "originalStartLine": None,
                                                "diffSide": "RIGHT",
                                                "comments": {
                                                    "pageInfo": {"hasNextPage": True, "endCursor": "comments-cursor-1"},
                                                    "nodes": comments,
                                                },
                                            }
                                        ],
                                    }
                                }
                            }
                        }
                    }
                else:
                    response = {
                        "data": {
                            "repository": {
                                "pullRequest": {
                                    "reviewThreads": {
                                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                                        "nodes": [
                                            {
                                                "id": "thread-2",
                                                "isResolved": True,
                                                "isOutdated": False,
                                                "path": "src/another.py",
                                                "line": 22,
                                                "originalLine": 22,
                                                "startLine": None,
                                                "originalStartLine": None,
                                                "diffSide": "RIGHT",
                                                "comments": {
                                                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                                                    "nodes": [make_comment(1000, include_commit)],
                                                },
                                            }
                                        ],
                                    }
                                }
                            }
                        }
                    }
            elif "node(id: $threadId)" in query:
                if comments_after:
                    nodes = [make_comment(51, include_commit)]
                    response = {
                        "data": {
                            "node": {
                                "comments": {
                                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                                    "nodes": nodes,
                                }
                            }
                        }
                    }
                else:
                    response = {
                        "data": {
                            "node": {
                                "comments": {
                                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                                    "nodes": [],
                                }
                            }
                        }
                    }
            else:
                response = {}

            print(json.dumps(response))
            """
        )
    )
    stub.chmod(0o755)
    return stub


def _env_with_stub(tmp_path: Path) -> dict:
    _write_gh_stub(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    return env


def test_pr_existing_comments_paginates_threads_and_comments(tmp_path):
    env = _env_with_stub(tmp_path)
    env["PR_REVIEW_REPO"] = "elastic/ai-github-actions"
    env["PR_REVIEW_PR_NUMBER"] = "714"

    result = subprocess.run(
        ["bash", str(PR_EXISTING_COMMENTS), "--summary"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Existing review threads: 2 total" in result.stdout
    assert "src/example.py" in result.stdout
    assert "src/another.py" in result.stdout
    assert "1 with replies" in result.stdout


def test_gh_get_review_threads_paginates_threads_and_comments(tmp_path):
    env = _env_with_stub(tmp_path)
    env["MENTION_REPO"] = "elastic/ai-github-actions"
    env["MENTION_PR_NUMBER"] = "714"

    result = subprocess.run(
        ["bash", str(GET_REVIEW_THREADS)],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    threads = json.loads(result.stdout)

    assert len(threads) == 2
    assert threads[0]["id"] == "thread-1"
    assert len(threads[0]["comments"]["nodes"]) == 51
    assert threads[1]["id"] == "thread-2"
