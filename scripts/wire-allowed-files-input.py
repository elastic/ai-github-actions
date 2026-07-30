#!/usr/bin/env python3
"""
Wire the create-pr-allowed-files workflow_call input to the safe-outputs handler config
in compiled lock files.

The gh-aw compiler generates allowed_files in the create_pull_request safe-output config
whenever the allowed-files field is present in the source workflow. Without this script
the config unconditionally includes allowed_files (either as [""] or ["**"]), whereas the
correct security behavior is:

  - When create-pr-allowed-files is NOT set: omit allowed_files entirely so that only
    the protected-files policy applies (gh-aw's default least-permissive behavior).
  - When create-pr-allowed-files IS set:    include allowed_files:[<pattern>] as usual.

Three substitutions are made per lock file:

  1. In the shell heredoc that writes the agent-job config.json.
     The compiler generates a shell env-var placeholder:
       "allowed_files":["${GH_AW_INPUT_CREATE_PR_ALLOWED_FILES}"],
     This is replaced with a GitHub Actions conditional expression so the key is
     omitted entirely when the input is empty:
       ${{ inputs.create-pr-allowed-files != '' && format('"allowed_files":["{0}"],', inputs.create-pr-allowed-files) || '' }}

  2. In the GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG YAML double-quoted env var (safe_outputs
     job).  Inside that string " is YAML-escaped as \".  After YAML parsing the \"
     sequences become ", so the embedded GitHub Actions expression evaluates identically
     to substitution (1) at runtime:
       \"allowed_files\":[\"${{ inputs.create-pr-allowed-files }}\"],
     becomes:
       ${{ inputs.create-pr-allowed-files != '' && format('\"allowed_files\":[\"{0}\"],', inputs.create-pr-allowed-files) || '' }}

All replacements produce valid JSON whether or not the input is set.

Usage:
  python3 ./scripts/wire-allowed-files-input.py
"""

import os

WORKFLOWS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".github", "workflows"
)

# ---------------------------------------------------------------------------
# Substitution 1 – config.json heredoc in the agent job (unescaped JSON).
# The compiler uses a shell env-var placeholder here; the gh-aw runtime
# substitutes it before the agent runs.  We replace the whole expression
# with a GitHub Actions conditional so the field is absent when unset.
# ---------------------------------------------------------------------------
OLD_HEREDOC = '"allowed_files":["${GH_AW_INPUT_CREATE_PR_ALLOWED_FILES}"],'
NEW_HEREDOC = (
    "${{ inputs.create-pr-allowed-files != '' "
    "&& format('\"allowed_files\":[\"" + "{0}" + "\"],', inputs.create-pr-allowed-files) "
    "|| '' }}"
)

# ---------------------------------------------------------------------------
# Substitution 2 – GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG YAML double-quoted
# string in the safe_outputs job.  Double-quotes are escaped as \" in the
# raw YAML file; after YAML parsing they become ", so the expression
# evaluates to the same JSON as substitution 1.
# ---------------------------------------------------------------------------
OLD_HANDLER = r'\"allowed_files\":[\"${{ inputs.create-pr-allowed-files }}\"],'
NEW_HANDLER = (
    r"${{ inputs.create-pr-allowed-files != '' "
    r"&& format('\"allowed_files\":[\"" + "{0}" + r"\"],', inputs.create-pr-allowed-files) "
    r"|| '' }}"
)


def process_file(path: str) -> bool:
    with open(path, encoding="utf-8") as fh:
        content = fh.read()

    # Only touch lock files that declare the create-pr-allowed-files input
    if "create-pr-allowed-files:" not in content:
        return False

    # Skip if neither old pattern is present (already wired or unaffected)
    if OLD_HEREDOC not in content and OLD_HANDLER not in content:
        return False

    new_content = content.replace(OLD_HEREDOC, NEW_HEREDOC)
    new_content = new_content.replace(OLD_HANDLER, NEW_HANDLER)

    if new_content == content:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_content)
    return True


def main() -> None:
    count = 0
    for filename in sorted(os.listdir(WORKFLOWS_DIR)):
        if not (filename.startswith("gh-aw-") and filename.endswith(".lock.yml")):
            continue
        path = os.path.join(WORKFLOWS_DIR, filename)
        if process_file(path):
            print(f"  \u2713 {filename}")
            count += 1

    print(f"\u2713 Wired create-pr-allowed-files in {count} lock file(s)")


if __name__ == "__main__":
    main()
