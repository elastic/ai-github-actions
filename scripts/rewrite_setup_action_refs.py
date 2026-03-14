#!/usr/bin/env python3
"""Rewrite gh-aw setup action refs in compiled lock files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: rewrite_setup_action_refs.py <repo> <ref>", file=sys.stderr)
        return 2

    repo = sys.argv[1].strip()
    ref = sys.argv[2].strip()

    if not repo or "/" not in repo:
        print(f"Invalid repo '{repo}'. Expected format owner/repo.", file=sys.stderr)
        return 2
    if not ref:
        print("Ref must not be empty.", file=sys.stderr)
        return 2

    pattern = re.compile(r"^(\s*uses:\s+)([^@\s]+/actions/setup)@([^\s#]+)(.*)$")
    updated_files = 0
    updated_lines = 0

    for path in Path(".").rglob("*.lock.yml"):
        original = path.read_text(encoding="utf-8")
        new_lines: list[str] = []
        file_changed = False

        for line in original.splitlines(keepends=True):
            match = pattern.match(line.rstrip("\n"))
            if not match:
                new_lines.append(line)
                continue

            prefix, _, _, suffix = match.groups()
            newline = "\n" if line.endswith("\n") else ""
            new_line = f"{prefix}{repo}/actions/setup@{ref}{suffix}{newline}"
            if new_line != line:
                file_changed = True
                updated_lines += 1
            new_lines.append(new_line)

        if file_changed:
            path.write_text("".join(new_lines), encoding="utf-8")
            updated_files += 1

    print(f"Updated {updated_lines} setup action reference(s) in {updated_files} lock file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
