#!/usr/bin/env python3
"""Wire minted create-token outputs into compiled GH-AW lock files.

The gh-aw compiler rejects mixed steps.* || secrets.* github-token expressions.
This post-process prefers create-token step outputs, then caller secrets, then
GITHUB_TOKEN. It also adds id-token: write to jobs that mint tokens.

Only lock files that declare the github-token-policy workflow_call input are
modified. The script is idempotent.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

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


def _job_mints_token(job_definition: object) -> bool:
    if not isinstance(job_definition, dict):
        return False
    steps = job_definition.get("steps")
    if not isinstance(steps, list):
        return False
    return any(
        isinstance(step, dict) and step.get("id") == "create-token"
        for step in steps
    )


def ensure_id_token_write(text: str) -> str:
    """Add id-token: write to permissions of jobs that mint create-token."""
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Expected a top-level YAML mapping")

    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        raise ValueError("Expected a top-level jobs mapping")

    changed = False
    for job_name, job_definition in jobs.items():
        if not _job_mints_token(job_definition):
            continue
        assert isinstance(job_definition, dict)
        permissions = job_definition.get("permissions")
        if not isinstance(permissions, dict):
            raise ValueError(
                f"Job '{job_name}' mints create-token but has no permissions mapping"
            )
        if permissions.get("id-token") != "write":
            permissions["id-token"] = "write"
            changed = True

    if not changed:
        return text

    return yaml.safe_dump(data, sort_keys=False)


def process_lock_file(path: Path) -> bool:
    """Rewrite one lock file. Return True when the file changed."""
    original = path.read_text(encoding="utf-8")
    if "github-token-policy:" not in original:
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
