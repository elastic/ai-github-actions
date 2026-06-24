#!/usr/bin/env python3
"""Post-process compiled lock files to expose report-failure-as-issue as a workflow_call input.

This script modifies each gh-aw-*.lock.yml file that:
  1. Has a `workflow_call:` trigger, AND
  2. Contains a hardcoded `GH_AW_FAILURE_REPORT_AS_ISSUE: "true"` env var

For each such file the script:
  a. Inserts a `report-failure-as-issue` boolean input (default: true) into the
     `workflow_call: inputs:` block.
  b. Replaces `GH_AW_FAILURE_REPORT_AS_ISSUE: "true"` with an expression that
     reads from the new input:
       GH_AW_FAILURE_REPORT_AS_ISSUE: ${{ inputs.report-failure-as-issue && 'true' || 'false' }}

Internal-only workflows (those without `workflow_call:`) are skipped intentionally
because they run directly in this repo and cannot accept external inputs.

Usage:
    python3 scripts/inject-report-failure-input.py [--check]

Options:
    --check   Dry-run mode: exit 1 if any file would be modified (used in CI to
              detect lock files that are out of date).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"

# The new input block to inject (4-space indented, matching existing inputs format).
_REPORT_FAILURE_INPUT = """\
      report-failure-as-issue:
        default: true
        description: When true, agent failures are reported as GitHub issues
        required: false
        type: boolean
"""

# Env-var line to replace.
_OLD_ENV = '          GH_AW_FAILURE_REPORT_AS_ISSUE: "true"'
_NEW_ENV = "          GH_AW_FAILURE_REPORT_AS_ISSUE: ${{ inputs.report-failure-as-issue && 'true' || 'false' }}"


def _should_process(content: str) -> bool:
    """Return True if the file needs processing."""
    if "workflow_call:" not in content:
        return False
    # Needs processing if: old env var present OR new input not yet injected OR old default format
    return (
        _OLD_ENV in content
        or "report-failure-as-issue:" not in content
        or 'report-failure-as-issue:\n        default: "true"\n' in content
    )


def _already_processed(content: str) -> bool:
    """Return True if the file has already been processed (input inserted AND env var replaced)."""
    # Check both conditions: new input present AND env var already replaced
    return (
        "report-failure-as-issue:" in content
        and _OLD_ENV not in content
        and 'report-failure-as-issue:\n        default: "true"' not in content
    )


def _inject_input(content: str) -> str:
    """Insert report-failure-as-issue into the workflow_call inputs block.

    We look for the first `    outputs:` or `    secrets:` line that appears
    inside the `workflow_call:` section and insert the new input just before it.
    """
    lines = content.splitlines(keepends=True)
    in_workflow_call = False
    inserted = False
    result: list[str] = []

    for i, line in enumerate(lines):
        # Detect entry into workflow_call block (2-space indented under `on:`)
        if re.match(r"^  workflow_call:\s*$", line):
            in_workflow_call = True

        if in_workflow_call and not inserted:
            # The first 4-space-indented key that is NOT `inputs:` signals the
            # end of the inputs block: could be `outputs:` or `secrets:`.
            if re.match(r"^    (outputs|secrets):\s*$", line):
                result.append(_REPORT_FAILURE_INPUT)
                inserted = True

        result.append(line)

        # Exit workflow_call block when we hit a top-level key (no leading spaces
        # or only one level of indentation: `permissions:`, `concurrency:`, etc.)
        if in_workflow_call and inserted and re.match(r"^[a-zA-Z]", line):
            in_workflow_call = False

    if not inserted:
        raise ValueError("Could not find insertion point for report-failure-as-issue input")

    return "".join(result)


def _replace_env_var(content: str) -> str:
    """Replace the hardcoded env var with an input-driven expression."""
    return content.replace(_OLD_ENV, _NEW_ENV)


def process_file(path: Path, *, check: bool = False) -> bool:
    """Process a single lock file.  Returns True if the file was (or would be) modified."""
    content = path.read_text(encoding="utf-8")

    if not _should_process(content):
        return False

    if _already_processed(content):
        return False

    new_content = content

    # Fix old string-format default if present (migration: "true" → true)
    _old_input_block = '      report-failure-as-issue:\n        default: "true"\n'
    _new_input_block = '      report-failure-as-issue:\n        default: true\n'
    if _old_input_block in new_content:
        new_content = new_content.replace(_old_input_block, _new_input_block)
    elif "report-failure-as-issue:" not in new_content:
        # Input not yet injected at all — insert it
        new_content = _inject_input(new_content)

    # Replace env var if still hardcoded
    if _OLD_ENV in new_content:
        new_content = _replace_env_var(new_content)

    if new_content == content:
        return False

    if check:
        print(f"  NEEDS UPDATE: {path.name}")
        return True

    path.write_text(new_content, encoding="utf-8")
    print(f"  ✓ {path.name}")
    return True


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    check_mode = "--check" in args

    if check_mode:
        print("Checking lock files for report-failure-as-issue input (dry-run)...")
    else:
        print("Injecting report-failure-as-issue input into lock files...")

    lock_files = sorted(WORKFLOWS_DIR.glob("*.lock.yml"))
    modified = 0
    errors = 0

    for path in lock_files:
        try:
            if process_file(path, check=check_mode):
                modified += 1
        except ValueError as exc:
            print(f"  ERROR processing {path.name}: {exc}", file=sys.stderr)
            errors += 1

    if check_mode:
        if modified:
            print(
                f"\n✗ {modified} file(s) need updating. Run "
                "'python3 scripts/inject-report-failure-input.py' to fix.",
                file=sys.stderr,
            )
            return 1
        print(f"✓ All {len(lock_files)} lock files are up to date.")
        return 0

    print(f"✓ Done. Modified {modified} file(s), {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
