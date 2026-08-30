#!/usr/bin/env python3
"""Extract compiled prompts from gh-aw lockfiles using YAML parsing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import re

import yaml


CREATE_PROMPT_STEP_NAME = "Create prompt with built-in context"
RUNTIME_INCLUDE_RE = re.compile(
    r'^\s*cat\s+["\']?(?P<path>[^"\']*/gh-aw/prompts/[^"\']+)["\']?\s*$'
)
HEREDOC_START_RE = re.compile(
    r'^\s*cat\s*<<-?\s*["\']?(?P<marker>[A-Za-z0-9_]+)["\']?\s*$'
)


def extract_prompts_from_run(run_script: str) -> str:
    """Extract heredoc content and runtime include placeholders from a run script."""
    lines: list[str] = []
    heredoc_end_marker: str | None = None

    for line in run_script.splitlines():
        if heredoc_end_marker is not None:
            if line.strip() == heredoc_end_marker:
                heredoc_end_marker = None
                continue
            lines.append(line)
            continue

        include_match = RUNTIME_INCLUDE_RE.match(line)
        if include_match:
            include_name = Path(include_match.group("path")).name
            lines.append(f"<!-- [RUNTIME INCLUDE: {include_name}] -->")
            lines.append("")
            continue

        heredoc_match = HEREDOC_START_RE.match(line)
        if heredoc_match:
            heredoc_end_marker = heredoc_match.group("marker")
            continue

    extracted = "\n".join(lines).rstrip()
    if not extracted:
        return ""
    return f"{extracted}\n"


def extract_lockfile_prompt(lockfile_path: Path) -> str:
    """Extract prompt content from a single lockfile's Create prompt step."""
    with lockfile_path.open("r", encoding="utf-8") as lockfile:
        data = yaml.safe_load(lockfile)

    if not isinstance(data, dict):
        return ""

    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return ""

    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_name = step.get("name")
            if not isinstance(step_name, str):
                continue
            if CREATE_PROMPT_STEP_NAME not in step_name:
                continue
            run_script = step.get("run")
            if not isinstance(run_script, str):
                continue
            return extract_prompts_from_run(run_script)

    return ""


def write_manifest(output_dir: Path, input_dir: Path, extracted_files: list[Path]) -> None:
    lines = [
        "# Prompt Audit Manifest",
        "",
        f"Extracted prompt text from {len(extracted_files)} lockfiles in `{input_dir}/`.",
        "",
        "| Workflow | Lines | File |",
        "| --- | --- | --- |",
    ]

    for prompt_file in extracted_files:
        workflow_name = prompt_file.name.removesuffix(".prompt.md")
        line_count = len(prompt_file.read_text(encoding="utf-8").splitlines())
        lines.append(f"| {workflow_name} | {line_count} | `{prompt_file}` |")

    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract agent prompt text from gh-aw .lock.yml files."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=".github/workflows",
        help="Directory containing gh-aw-*.lock.yml files.",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="/tmp/prompt-audit",
        help="Directory where extracted *.prompt.md files will be written.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_files: list[Path] = []
    for lockfile_path in sorted(input_dir.glob("gh-aw-*.lock.yml")):
        workflow_name = lockfile_path.name.removeprefix("gh-aw-").removesuffix(".lock.yml")
        output_file = output_dir / f"{workflow_name}.prompt.md"
        prompt_text = extract_lockfile_prompt(lockfile_path)

        if prompt_text:
            output_file.write_text(prompt_text, encoding="utf-8")
            extracted_files.append(output_file)
        elif output_file.exists():
            output_file.unlink()

    write_manifest(output_dir, input_dir, extracted_files)

    print(f"Extracted prompts from {len(extracted_files)} lockfiles -> {output_dir}/")
    for path in sorted(output_dir.glob("*")):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
