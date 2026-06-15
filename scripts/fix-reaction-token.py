#!/usr/bin/env python3
"""Fix reaction token references in compiled lock files.

The gh-aw compiler generates reaction steps with github-token: ${{ secrets.GITHUB_TOKEN }},
but this should use the automatic github.token instead for proper permissions.
This script post-processes all .lock.yml files to fix this issue.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    """Fix reaction token references in all .lock.yml files."""
    # Pattern to match the reaction step's github-token line
    # We need to be specific to only match the reaction steps, not other uses of github-token
    pattern = re.compile(
        r"^(\s+github-token:\s+\$\{\{\s+)secrets\.GITHUB_TOKEN(\s+\}\})$"
    )
    
    updated_files = 0
    updated_lines = 0
    
    # Find all .lock.yml files in .github/workflows
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("Error: .github/workflows directory not found", file=sys.stderr)
        return 1
    
    for path in workflows_dir.glob("*.lock.yml"):
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        new_lines: list[str] = []
        file_changed = False
        in_reaction_step = False
        
        for i, line in enumerate(lines):
            # Detect if we're in a reaction step by looking for the step name
            if "Add eyes reaction for immediate feedback" in line or "Add reaction for immediate feedback" in line:
                in_reaction_step = True
            # Exit reaction step when we hit the next step (starts with "- name:")
            elif in_reaction_step and line.strip().startswith("- name:"):
                in_reaction_step = False
            
            # Only replace github-token if we're in a reaction step
            if in_reaction_step:
                match = pattern.match(line.rstrip("\n"))
                if match:
                    prefix, suffix = match.groups()
                    newline = "\n" if line.endswith("\n") else ""
                    # Replace secrets.GITHUB_TOKEN with github.token
                    new_line = f"{prefix}github.token{suffix}{newline}"
                    if new_line != line:
                        file_changed = True
                        updated_lines += 1
                        print(f"  Fixed token reference in {path.name}")
                    new_lines.append(new_line)
                    continue
            
            new_lines.append(line)
        
        if file_changed:
            path.write_text("".join(new_lines), encoding="utf-8")
            updated_files += 1
    
    print(f"\n✓ Updated {updated_lines} token reference(s) in {updated_files} workflow file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
