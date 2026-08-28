#!/usr/bin/env python3
"""Wire minted create-token outputs into compiled GH-AW lock files.

The gh-aw compiler rejects mixed steps.* || secrets.* github-token expressions.
This post-process prefers create-token step outputs, then caller secrets, then
GITHUB_TOKEN. It also adds id-token: write to jobs that mint tokens.

Only lock files that declare the mint-ephemeral-token workflow_call input are
modified. The script is idempotent.
"""

from __future__ import annotations

import sys
from pathlib import Path

MINTED_PREFIX = "steps.create-token.outputs.token || "

# Longer fallback chains first so the short GH_AW_GITHUB_TOKEN suffix is not
# rewritten inside MCP-token expressions.
REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (
        "${{ secrets.GH_AW_GITHUB_MCP_SERVER_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}",
        "${{ "
        + MINTED_PREFIX
        + "secrets.GH_AW_GITHUB_MCP_SERVER_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}",
    ),
    (
        "${{ secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}",
        "${{ " + MINTED_PREFIX + "secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}",
    ),
)

ID_TOKEN_LINE = "      id-token: write"


def wire_token_expressions(text: str) -> str:
    """Prefer minted step outputs in known GH-AW token fallback expressions."""
    rewritten: list[str] = []
    for line in text.splitlines(keepends=True):
        if "create-token.outputs.token" in line:
            rewritten.append(line)
            continue
        for old, new in REPLACEMENTS:
            if old in line:
                line = line.replace(old, new)
                break
        rewritten.append(line)
    return "".join(rewritten)


def _job_blocks(text: str) -> list[tuple[int, int]]:
    """Return (start, end) line-index spans for top-level jobs.* blocks."""
    lines = text.splitlines(keepends=True)
    jobs_idx = None
    for i, line in enumerate(lines):
        if line == "jobs:\n" or line == "jobs:":
            jobs_idx = i
            break
    if jobs_idx is None:
        return []

    starts: list[int] = []
    for i in range(jobs_idx + 1, len(lines)):
        line = lines[i]
        if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":"):
            starts.append(i)
            continue
        if line and not line.startswith(" ") and line.strip():
            break
    spans: list[tuple[int, int]] = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(lines)
        spans.append((start, end))
    return spans


def ensure_id_token_write(text: str) -> str:
    """Add id-token: write to permissions of jobs that mint create-token."""
    lines = text.splitlines(keepends=True)
    spans = _job_blocks(text)
    inserts: list[tuple[int, str]] = []
    for start, end in spans:
        block = "".join(lines[start:end])
        if "id: create-token" not in block:
            continue
        if "id-token: write" in block:
            continue
        perm_rel = None
        for j, line in enumerate(lines[start:end]):
            if line == "    permissions:\n":
                perm_rel = j
                break
        if perm_rel is None:
            continue
        inserts.append((start + perm_rel + 1, ID_TOKEN_LINE + "\n"))

    for idx, line in sorted(inserts, reverse=True):
        lines.insert(idx, line)
    return "".join(lines)


def process_lock_file(path: Path) -> bool:
    """Rewrite one lock file. Return True when the file changed."""
    original = path.read_text(encoding="utf-8")
    if "mint-ephemeral-token:" not in original:
        return False
    updated = wire_token_expressions(original)
    updated = ensure_id_token_write(updated)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    workflows = repo_root / ".github" / "workflows"
    changed = 0
    for lock_file in sorted(workflows.glob("gh-aw-*.lock.yml")):
        if process_lock_file(lock_file):
            print(f"  ✓ {lock_file.name}")
            changed += 1
    print(f"✓ Wired ephemeral token outputs in {changed} lock file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
