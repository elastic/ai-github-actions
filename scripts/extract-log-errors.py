#!/usr/bin/env python3
"""
Extract errors and failures from GitHub Actions log files.

Reads log files produced by fetch-workflow-logs.py and outputs each error/failure
with surrounding context lines, suitable for agent analysis.

Usage:
  python3 scripts/extract-log-errors.py <log-dir-or-file> [options]

Options:
  --context N           Lines of context before/after each match (default: 5)
  --patterns FILE       File with additional grep patterns (one per line)
  --manifest FILE       Path to manifest.json from fetch-workflow-logs.py
  --output FILE         Write JSON summary to file (default: stdout)

The script searches for common failure patterns:
  - "##[error]", "Error:", "fatal:", "error:", "FAILED", "failure"
  - Exit code lines: "exited with exit code [^0]"
  - GitHub Actions step failure markers
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Patterns that indicate errors or failures in GitHub Actions logs
DEFAULT_PATTERNS = [
    r"##\[error\]",
    r"##\[warning\]",
    r"\bError:",
    r"\bfatal:",
    r"\bFAILED\b",
    r"exited with exit code [^0]",
    r"Process completed with exit code [^0]",
    r"\bRun failed\b",
    r"The process '.*' failed",
]


def find_log_files(path: str) -> list[str]:
    """Recursively find all .txt log files under path."""
    result = []
    p = Path(path)
    if p.is_file():
        return [str(p)]
    for f in sorted(p.rglob("*.txt")):
        result.append(str(f))
    return result


def extract_matches(filepath: str, patterns: list[re.Pattern], context: int) -> list[dict]:
    """Return a list of match records with surrounding context."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        return [{"file": filepath, "error": str(e)}]

    matched_lines = set()
    for i, line in enumerate(lines):
        for pat in patterns:
            if pat.search(line):
                matched_lines.add(i)
                break

    if not matched_lines:
        return []

    # Group nearby matches into blocks
    blocks: list[tuple[int, int]] = []
    for lineno in sorted(matched_lines):
        start = max(0, lineno - context)
        end = min(len(lines) - 1, lineno + context)
        if blocks and start <= blocks[-1][1] + 1:
            blocks[-1] = (blocks[-1][0], end)
        else:
            blocks.append((start, end))

    results = []
    for start, end in blocks:
        snippet = "".join(lines[start:end + 1])
        results.append({
            "file": filepath,
            "start_line": start + 1,
            "end_line": end + 1,
            "snippet": snippet.rstrip(),
        })
    return results


def load_manifest(manifest_path: str) -> list[dict]:
    with open(manifest_path) as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract errors from GitHub Actions log files.")
    parser.add_argument("log_path", nargs="?", default=None,
                        help="Directory or file containing log files")
    parser.add_argument("--context", type=int, default=5,
                        help="Lines of context around each match (default: 5)")
    parser.add_argument("--patterns", default=None,
                        help="File with additional patterns (one per line)")
    parser.add_argument("--manifest", default=None,
                        help="Manifest JSON from fetch-workflow-logs.py")
    parser.add_argument("--output", default=None,
                        help="Write JSON output to file (default: stdout)")
    args = parser.parse_args()

    patterns = [re.compile(p) for p in DEFAULT_PATTERNS]
    if args.patterns:
        with open(args.patterns) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(re.compile(line))

    # Collect log files
    log_files: list[str] = []
    run_meta: dict[str, dict] = {}

    if args.manifest:
        manifest = load_manifest(args.manifest)
        for entry in manifest:
            run_id = str(entry["run_id"])
            run_meta[run_id] = {
                "run_id": entry["run_id"],
                "conclusion": entry.get("conclusion", ""),
                "created_at": entry.get("created_at", ""),
                "html_url": entry.get("html_url", ""),
            }
            for f in entry.get("log_files", []):
                log_files.append(f)
    elif args.log_path:
        log_files = find_log_files(args.log_path)
    else:
        print("Error: provide a log path or --manifest", file=sys.stderr)
        sys.exit(1)

    if not log_files:
        print("No log files found.", file=sys.stderr)
        sys.exit(0)

    print(f"Scanning {len(log_files)} log file(s)...", file=sys.stderr)

    all_matches: list[dict] = []
    for filepath in log_files:
        matches = extract_matches(filepath, patterns, args.context)
        all_matches.extend(matches)

    # Attach run metadata where available
    for m in all_matches:
        filepath = m.get("file", "")
        # Try to extract run_id from path (e.g. /tmp/gh-aw/logs/12345678/...)
        parts = Path(filepath).parts
        for part in parts:
            if part in run_meta:
                m["run"] = run_meta[part]
                break

    summary = {
        "total_files_scanned": len(log_files),
        "total_matches": len(all_matches),
        "matches": all_matches,
    }

    output_text = json.dumps(summary, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Results written to {args.output}", file=sys.stderr)
        print(args.output)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
