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
    r"(?i)\berror:",
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
    """Return match records with surrounding context from a readable log file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []

    matched_lines = find_matching_lines(lines, patterns)
    if not matched_lines:
        return []

    blocks = coalesce_blocks(matched_lines, len(lines), context)
    return format_match_results(filepath, lines, blocks)


def find_matching_lines(lines: list[str], patterns: list[re.Pattern]) -> set[int]:
    matched_lines: set[int] = set()
    for i, line in enumerate(lines):
        for pattern in patterns:
            if pattern.search(line):
                matched_lines.add(i)
                break
    return matched_lines


def coalesce_blocks(matched_lines: set[int], line_count: int, context: int) -> list[tuple[int, int]]:
    blocks: list[tuple[int, int]] = []
    for lineno in sorted(matched_lines):
        start = max(0, lineno - context)
        end = min(line_count - 1, lineno + context)
        if blocks and start <= blocks[-1][1] + 1:
            blocks[-1] = (blocks[-1][0], end)
        else:
            blocks.append((start, end))
    return blocks


def format_match_results(filepath: str, lines: list[str], blocks: list[tuple[int, int]]) -> list[dict]:
    results = []
    for start, end in blocks:
        snippet = "".join(lines[start:end + 1])
        results.append(
            {
                "file": filepath,
                "start_line": start + 1,
                "end_line": end + 1,
                "snippet": snippet.rstrip(),
            }
        )
    return results


def load_manifest(manifest_path: str) -> list[dict]:
    with open(manifest_path) as f:
        return json.load(f)


def build_patterns(pattern_file: str | None) -> list[re.Pattern]:
    patterns = [re.compile(pattern) for pattern in DEFAULT_PATTERNS]
    if not pattern_file:
        return patterns

    with open(pattern_file) as f:
        for line in f:
            candidate = line.strip()
            if candidate and not candidate.startswith("#"):
                patterns.append(re.compile(candidate))
    return patterns


def collect_log_files(
    log_path: str | None, manifest_path: str | None
) -> tuple[list[str], dict[str, dict], dict[str, dict]]:
    if manifest_path:
        return collect_log_files_from_manifest(load_manifest(manifest_path))
    if log_path:
        return find_log_files(log_path), {}, {}
    print("Error: provide a log path or --manifest", file=sys.stderr)
    sys.exit(1)


def collect_log_files_from_manifest(
    manifest: list[dict],
) -> tuple[list[str], dict[str, dict], dict[str, dict]]:
    log_files: list[str] = []
    run_meta: dict[str, dict] = {}
    file_run_meta: dict[str, dict] = {}

    for entry in manifest:
        run_id = str(entry["run_id"])
        run_record = {
            "run_id": entry["run_id"],
            "conclusion": entry.get("conclusion", ""),
            "created_at": entry.get("created_at", ""),
            "html_url": entry.get("html_url", ""),
        }
        run_meta[run_id] = run_record
        for log_file in entry.get("log_files", []):
            log_files.append(log_file)
            file_run_meta[log_file] = run_record

    return log_files, run_meta, file_run_meta


def attach_run_metadata(
    matches: list[dict], run_meta: dict[str, dict], file_run_meta: dict[str, dict]
) -> None:
    for match in matches:
        filepath = match.get("file", "")
        if filepath in file_run_meta:
            match["run"] = file_run_meta[filepath]
            continue
        parts = Path(filepath).parts
        for part in parts:
            if part in run_meta:
                match["run"] = run_meta[part]
                break


def emit_output(summary: dict, output_path: str | None) -> None:
    output_text = json.dumps(summary, indent=2)
    if output_path:
        with open(output_path, "w") as f:
            f.write(output_text)
        print(f"Results written to {output_path}", file=sys.stderr)
        print(output_path)
        return
    print(output_text)


def emit_empty_output(output_path: str | None) -> None:
    if not output_path:
        return
    empty = {
        "total_files_scanned": 0,
        "total_matches": 0,
        "matches": [],
        "file_errors": [],
    }
    with open(output_path, "w") as f:
        json.dump(empty, f, indent=2)


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

    patterns = build_patterns(args.patterns)
    log_files, run_meta, file_run_meta = collect_log_files(args.log_path, args.manifest)

    if not log_files:
        print("No log files found.", file=sys.stderr)
        emit_empty_output(args.output)
        sys.exit(0)

    print(f"Scanning {len(log_files)} log file(s)...", file=sys.stderr)

    all_matches: list[dict] = []
    file_errors: list[dict] = []
    for filepath in log_files:
        if not os.path.isfile(filepath):
            file_errors.append({"file": filepath, "error": "File not found"})
            continue
        if not os.access(filepath, os.R_OK):
            file_errors.append({"file": filepath, "error": "File is not readable"})
            continue

        matches = extract_matches(filepath, patterns, args.context)
        all_matches.extend(matches)

    attach_run_metadata(all_matches, run_meta, file_run_meta)
    attach_run_metadata(file_errors, run_meta, file_run_meta)

    summary = {
        "total_files_scanned": len(log_files),
        "total_matches": len(all_matches),
        "matches": all_matches,
        "file_errors": file_errors,
    }

    emit_output(summary, args.output)


if __name__ == "__main__":
    main()
