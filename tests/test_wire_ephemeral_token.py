"""Tests for scripts/wire-ephemeral-token.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "wire-ephemeral-token.py"
SPEC = importlib.util.spec_from_file_location("wire_ephemeral_token", MODULE_PATH)
assert SPEC and SPEC.loader
wire = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wire)


SAMPLE_LOCK = """on:
  workflow_call:
    inputs:
      github-token-policy:
        type: string
jobs:
  safe_outputs:
    permissions:
      issues: write
    steps:
      - id: create-token
        uses: elastic/oblt-actions/github/create-token@v1
      - name: Process Safe Outputs
        with:
          github-token: ${{ secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}
  detection:
    permissions:
      contents: read
    steps:
      - name: Scan
        with:
          github-token: ${{ secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}
"""


def test_wire_token_expressions_is_idempotent() -> None:
    once = wire.wire_token_expressions(SAMPLE_LOCK)
    twice = wire.wire_token_expressions(once)
    assert once == twice
    assert "steps.create-token.outputs.token" in once
    assert "create-token-auto" not in once


def test_ensure_id_token_write_only_on_minting_jobs() -> None:
    updated = wire.ensure_id_token_write(SAMPLE_LOCK)
    parsed = yaml.safe_load(updated)
    assert parsed["jobs"]["safe_outputs"]["permissions"]["id-token"] == "write"
    assert "id-token" not in parsed["jobs"]["detection"]["permissions"]


def test_ensure_id_token_write_raises_for_missing_permissions() -> None:
    source = """jobs:
  safe_outputs:
    steps:
      - id: create-token
        uses: elastic/oblt-actions/github/create-token@v1
"""
    with pytest.raises(ValueError, match="has no permissions mapping"):
        wire.ensure_id_token_write(source)


def test_wire_mcp_chain_is_not_double_prefixed() -> None:
    source = (
        "          github-token: ${{ secrets.GH_AW_GITHUB_MCP_SERVER_TOKEN || "
        "secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}\n"
    )
    once = wire.wire_token_expressions(source)
    twice = wire.wire_token_expressions(once)
    assert once == twice
    assert once.count("create-token.outputs.token") == 1
    assert "create-token-auto" not in once
    assert "GH_AW_GITHUB_MCP_SERVER_TOKEN" in once


def test_minted_prefix_uses_shared_policy_only() -> None:
    assert wire.MINTED_PREFIX == "steps.create-token.outputs.token || "
    assert "create-token-auto" not in wire.MINTED_PREFIX


def test_process_lock_file_skips_without_input(tmp_path: Path) -> None:
    lock = tmp_path / "gh-aw-other.lock.yml"
    lock.write_text("jobs:\n  run:\n    steps: []\n", encoding="utf-8")
    assert wire.process_lock_file(lock) is False


def test_ensure_id_token_write_handles_indentation_variants() -> None:
    source = """jobs:
    safe_outputs:
        permissions:
            issues: write
        steps:
            - id: create-token
              uses: elastic/oblt-actions/github/create-token@v1
"""
    updated = wire.ensure_id_token_write(source)
    parsed = yaml.safe_load(updated)
    assert parsed["jobs"]["safe_outputs"]["permissions"]["id-token"] == "write"
