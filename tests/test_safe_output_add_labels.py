"""Regression tests for add_labels allowlist pre-sanitize.

After gh-aw ~v0.83.4, agents emit label objects
``{name, confidence, rationale}`` instead of plain strings. The shared
fragment must resolve ``.name`` so allowlist matching does not turn
objects into ``"[object Object]"`` and drop every label.
"""

from __future__ import annotations

import json
import re
import subprocess
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FRAGMENT = (
    REPO_ROOT
    / ".github"
    / "workflows"
    / "gh-aw-fragments"
    / "safe-output-add-labels.md"
)
PR_LABELER = REPO_ROOT / ".github" / "workflows" / "gh-aw-pr-labeler.md"
LOCK_FILES = [
    REPO_ROOT / ".github" / "workflows" / "gh-aw-dependency-review.lock.yml",
    REPO_ROOT / ".github" / "workflows" / "gh-aw-issue-triage.lock.yml",
    REPO_ROOT / ".github" / "workflows" / "gh-aw-pr-labeler.lock.yml",
]


def _extract_sanitize_script(markdown_path: Path) -> str:
    text = markdown_path.read_text()
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"Expected YAML frontmatter in {markdown_path}"
    frontmatter = yaml.safe_load(parts[1])
    steps = frontmatter["safe-outputs"]["steps"]
    sanitize = next(
        step for step in steps if "sanitize" in step.get("name", "").lower()
    )
    script = sanitize["with"]["script"]
    assert "typeof v === 'object'" in script, (
        f"{markdown_path}: sanitize must resolve object-shaped labels via .name"
    )
    assert "String(v).trim()" not in script, (
        f"{markdown_path}: must not use String(v) on label entries "
        "(turns objects into '[object Object]')"
    )
    return script


def _run_sanitize(
    script: str,
    *,
    items: list[dict],
    classification_labels: str,
) -> dict:
    """Execute the github-script body with minimal fs/core stubs via node."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        output_path = Path(tmp) / "agent-output.json"
        script_path = Path(tmp) / "sanitize.js"
        harness_path = Path(tmp) / "harness.js"
        output_path.write_text(json.dumps({"items": items}))
        # github-script bodies use top-level `return`; wrap in a function.
        script_path.write_text(
            "module.exports = function run(core) {\n" + script + "\n};\n"
        )
        harness_path.write_text(
            textwrap.dedent(
                """\
                const fs = require('fs');
                const outputPath = process.env.GH_AW_AGENT_OUTPUT;
                const core = { info() {}, warning() {} };
                const run = require(process.env.TEST_SANITIZE_MODULE);
                run(core);
                process.stdout.write(fs.readFileSync(outputPath, 'utf8'));
                """
            )
        )
        env = {
            **os.environ,
            "GH_AW_AGENT_OUTPUT": str(output_path),
            "CLASSIFICATION_LABELS": classification_labels,
            "ALLOWED_LABELS": classification_labels,
            "TEST_SANITIZE_MODULE": str(script_path),
        }
        result = subprocess.run(
            ["node", str(harness_path)],
            capture_output=True,
            text=True,
            env=env,
            timeout=15,
            check=False,
        )
        assert result.returncode == 0, (
            f"sanitize script failed:\nstdout={result.stdout}\nstderr={result.stderr}"
        )
        return json.loads(result.stdout)


@pytest.fixture(scope="module")
def fragment_script() -> str:
    return _extract_sanitize_script(FRAGMENT)


def test_fragment_keeps_string_labels(fragment_script: str) -> None:
    out = _run_sanitize(
        fragment_script,
        items=[
            {
                "type": "add_labels",
                "item_number": 1,
                "labels": ["oblt-aw/ai/merge-ready", "not-allowed"],
            }
        ],
        classification_labels="oblt-aw/ai/merge-ready",
    )
    assert out["items"] == [
        {
            "type": "add_labels",
            "item_number": 1,
            "labels": ["oblt-aw/ai/merge-ready"],
        }
    ]


def test_fragment_keeps_object_shaped_labels(fragment_script: str) -> None:
    """Regression: object labels must not become '[object Object]'."""
    out = _run_sanitize(
        fragment_script,
        items=[
            {
                "type": "add_labels",
                "item_number": 641,
                "labels": [
                    {
                        "confidence": "HIGH",
                        "name": "oblt-aw/ai/merge-ready",
                        "rationale": "low risk dependency bump",
                    }
                ],
            },
            {
                "type": "add_comment",
                "body": "analysis",
            },
        ],
        classification_labels="oblt-aw/ai/merge-ready",
    )
    assert out["items"][0] == {
        "type": "add_labels",
        "item_number": 641,
        "labels": ["oblt-aw/ai/merge-ready"],
    }
    assert out["items"][1]["type"] == "add_comment"


def test_fragment_drops_disallowed_object_labels(fragment_script: str) -> None:
    out = _run_sanitize(
        fragment_script,
        items=[
            {
                "type": "add_labels",
                "item_number": 2,
                "labels": [{"name": "evil-label", "confidence": "HIGH"}],
            }
        ],
        classification_labels="oblt-aw/ai/merge-ready",
    )
    assert out["items"] == []


def test_pr_labeler_source_resolves_object_labels() -> None:
    script = _extract_sanitize_script(PR_LABELER)
    out = _run_sanitize(
        script,
        items=[
            {
                "type": "add_labels",
                "labels": [{"name": "needs-docs", "confidence": "MEDIUM"}],
            }
        ],
        classification_labels="needs-docs,needs-tests",
    )
    assert out["items"][0]["labels"] == ["needs-docs"]


@pytest.mark.parametrize("lock_path", LOCK_FILES, ids=lambda p: p.name)
def test_compiled_locks_resolve_object_labels(lock_path: Path) -> None:
    text = lock_path.read_text()
    assert "typeof v === 'object'" in text, (
        f"{lock_path.name} missing object-label sanitize; run `make compile`"
    )
    assert not re.search(
        r"\.map\(\(v\) => String\(v\)\.trim\(\)\)",
        text,
    ), f"{lock_path.name} still uses String(v).trim() label sanitize"
