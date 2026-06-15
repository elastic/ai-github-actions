#!/usr/bin/env python3
"""Fix reaction step github-token references in compiled lock files.

The gh-aw compiler generates reaction steps with:
    github-token: ${{ secrets.GITHUB_TOKEN }}

This should be:
    github-token: ${{ github.token }}

Using secrets.GITHUB_TOKEN refers to a user-defined secret that may not exist,
while github.token is the automatic token provided by GitHub Actions with the
permissions specified in the workflow's permissions section.

This script post-processes compiled .lock.yml files to fix the token reference.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    """Fix github-token references in reaction steps."""
    # Pattern to match github-token in reaction steps
    # We look for the specific pattern where GH_AW_REACTION is set
    # and github-token uses secrets.GITHUB_TOKEN
    pattern = re.compile(
        r'^(\s+github-token:\s+)\$\{\{\s*secrets\.GITHUB_TOKEN\s*\}\}(.*)$'
    )
    
    updated_files = 0
    updated_lines = 0
    
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print(f"Error: {workflows_dir} directory not found", file=sys.stderr)
        return 1
    
    for path in workflows_dir.glob("*.lock.yml"):
        original = path.read_text(encoding="utf-8")
        new_lines: list[str] = []
        file_changed = False
        in_reaction_context = False
        
        for line_no, line in enumerate(original.splitlines(keepends=True), 1):
            # Track if we're in a reaction step context
            if "GH_AW_REACTION:" in line:
                in_reaction_context = True
            elif in_reaction_context and line.strip() and not line.startswith(" "):
                # Exit reaction context when we hit a non-indented line
                in_reaction_context = False
            
            # Only fix github-token if we're in a reaction context
            if in_reaction_context:
                match = pattern.match(line.rstrip("\n"))
                if match:
                    prefix = match.group(1)
                    suffix = match.group(2)
                    new_line = f"{prefix}${{{{ github.token }}}}{suffix}\n"
                    new_lines.append(new_line)
                    file_changed = True
                    updated_lines += 1
                    print(f"  {path.name}:{line_no}: Fixed github-token reference")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if file_changed:
            path.write_text("".join(new_lines), encoding="utf-8")
            updated_files += 1
            print(f"✓ Updated {path.name}")
    
    if updated_files > 0:
        print(f"\n✓ Fixed {updated_lines} github-token reference(s) in {updated_files} file(s)")
    else:
        print("No github-token references to fix")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
