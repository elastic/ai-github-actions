#!/usr/bin/env python3
"""
Download job logs for a GitHub Actions workflow.

Usage:
  python3 scripts/fetch-workflow-logs.py <workflow-name> [options]

Options:
  --repo OWNER/REPO     Repository (default: $GITHUB_REPOSITORY)
  --last N              Download logs from the last N runs (default: 20)
  --since DATE          Only include runs on or after this date (ISO 8601, e.g. 2025-01-01)
  --until DATE          Only include runs before or on this date (ISO 8601)
  --conclusion STATUS   Filter by conclusion: success, failure, cancelled, skipped (default: failure)
  --output-dir DIR      Directory to save logs (default: /tmp/gh-aw/logs)
  --token TOKEN         GitHub token (default: $GH_TOKEN or $GITHUB_TOKEN)

Each run's logs are saved as individual .txt files under output-dir/<run_id>/.
"""

import argparse
import io
import json
import os
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone


def github_api(path: str, token: str, accept: str = "application/vnd.github+json") -> bytes:
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def list_workflow_runs(repo: str, workflow: str, token: str, since: str | None, until: str | None,
                       conclusion: str | None, last: int) -> list[dict]:
    """Return up to `last` workflow runs matching the filters."""
    runs = []
    page = 1
    per_page = 100
    while len(runs) < last:
        path = f"/repos/{repo}/actions/workflows/{workflow}/runs?per_page={per_page}&page={page}"
        data = json.loads(github_api(path, token))
        batch = data.get("workflow_runs", [])
        if not batch:
            break
        for run in batch:
            if conclusion and run.get("conclusion") != conclusion:
                continue
            created = run.get("created_at", "")
            if since and created < since:
                # Runs are sorted newest-first; once we go past since, stop paging
                return runs
            if until and created > until:
                continue
            runs.append(run)
            if len(runs) >= last:
                break
        page += 1
    return runs


def download_run_logs(repo: str, run_id: int, token: str, output_dir: str) -> list[str]:
    """Download and unzip logs for a run. Returns list of saved file paths."""
    run_dir = os.path.join(output_dir, str(run_id))
    os.makedirs(run_dir, exist_ok=True)
    try:
        data = github_api(f"/repos/{repo}/actions/runs/{run_id}/logs", token,
                          accept="application/vnd.github+json")
    except Exception as e:
        print(f"  Warning: could not download logs for run {run_id}: {e}", file=sys.stderr)
        return []

    saved = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            if not name.endswith(".txt"):
                continue
            dest = os.path.join(run_dir, name.replace("/", "_"))
            content = zf.read(name)
            with open(dest, "wb") as f:
                f.write(content)
            saved.append(dest)
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description="Download GitHub Actions workflow logs.")
    parser.add_argument("workflow", help="Workflow file name (e.g. trigger-pr-review.yml) or workflow ID")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                        help="Owner/repo (default: $GITHUB_REPOSITORY)")
    parser.add_argument("--last", type=int, default=20,
                        help="Number of recent runs to download (default: 20)")
    parser.add_argument("--since", default=None,
                        help="Only include runs on or after this date (ISO 8601)")
    parser.add_argument("--until", default=None,
                        help="Only include runs before or on this date (ISO 8601)")
    parser.add_argument("--conclusion", default="failure",
                        help="Filter by conclusion (default: failure; use 'any' for all)")
    parser.add_argument("--output-dir", default="/tmp/gh-aw/logs",
                        help="Directory to save logs (default: /tmp/gh-aw/logs)")
    parser.add_argument("--token", default=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", ""),
                        help="GitHub token (default: $GH_TOKEN or $GITHUB_TOKEN)")
    args = parser.parse_args()

    if not args.repo:
        print("Error: --repo is required (or set $GITHUB_REPOSITORY)", file=sys.stderr)
        sys.exit(1)
    if not args.token:
        print("Error: --token is required (or set $GH_TOKEN / $GITHUB_TOKEN)", file=sys.stderr)
        sys.exit(1)

    conclusion_filter = None if args.conclusion == "any" else args.conclusion

    print(f"Listing runs for {args.workflow} in {args.repo}...", file=sys.stderr)
    runs = list_workflow_runs(
        repo=args.repo,
        workflow=args.workflow,
        token=args.token,
        since=args.since,
        until=args.until,
        conclusion=conclusion_filter,
        last=args.last,
    )

    if not runs:
        print("No matching runs found.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(runs)} matching run(s). Downloading logs to {args.output_dir}...", file=sys.stderr)
    os.makedirs(args.output_dir, exist_ok=True)

    results = []
    for run in runs:
        run_id = run["id"]
        created = run.get("created_at", "")
        conclusion = run.get("conclusion", "")
        url = run.get("html_url", "")
        print(f"  Run {run_id} ({conclusion}, {created}): {url}", file=sys.stderr)
        files = download_run_logs(args.repo, run_id, args.token, args.output_dir)
        results.append({
            "run_id": run_id,
            "conclusion": conclusion,
            "created_at": created,
            "html_url": url,
            "log_files": files,
        })

    # Write a manifest so callers know what was downloaded
    manifest_path = os.path.join(args.output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Manifest written to {manifest_path}", file=sys.stderr)
    print(manifest_path)


if __name__ == "__main__":
    main()
