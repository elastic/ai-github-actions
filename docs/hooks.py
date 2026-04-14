"""MkDocs hook: generate individual documentation pages for each gh-agent-workflow.

For each subdirectory under gh-agent-workflows/ that contains both a README.md
and an example.yml, this hook generates a docs page embedding the README content
followed by the example workflow as a YAML code block.  The "See [example.yml]"
sentence is dropped from the README body since the example is shown inline.
"""

import atexit
import re
import shutil
import tempfile
from pathlib import Path

from mkdocs.structure.files import File

_tmp_dir: str | None = None

_WORKFLOWS_DIR = "gh-agent-workflows"
_DOCS_DEST = "workflows/gh-agent-workflows"
_GITHUB_REPO = "https://github.com/elastic/ai-github-actions"


def _workflow_source_link(example_content: str) -> str | None:
    """Return a Markdown link to the source workflow .md file, or None.

    Parses the ``uses:`` line in the example workflow to determine which
    compiled ``.lock.yml`` — and therefore which source ``.md`` — the
    workflow uses.
    """
    match = re.search(
        r"uses:\s+elastic/ai-github-actions/\.github/workflows/(gh-aw-[^.]+)\.lock\.yml",
        example_content,
    )
    if not match:
        return None
    filename = f"{match.group(1)}.md"
    url = f"{_GITHUB_REPO}/blob/main/.github/workflows/{filename}"
    return f"[`{filename}`]({url})"


def _rewrite_sibling_workflow_links(readme: str) -> str:
    """Rewrite sibling workflow links to generated docs pages.

    The generated workflow docs live under docs/workflows/gh-agent-workflows/.
    Rewrite source-tree links so they resolve from that location:
    - ../other-workflow/README.md -> other-workflow.md
    - ../other-workflow/ -> other-workflow.md
    - ../../docs/workflows/<page>.md -> ../<page>.md
    """

    def replace_link(match: re.Match[str]) -> str:
        link_text = match.group(1)
        target = match.group(2)

        readme_match = re.fullmatch(r"\.\./([a-z0-9-]+)/README\.md(#.*)?", target)
        if readme_match:
            slug = readme_match.group(1)
            anchor = readme_match.group(2) or ""
            return f"[{link_text}]({slug}.md{anchor})"

        dir_match = re.fullmatch(r"\.\./([a-z0-9-]+)/(#.*)?", target)
        if dir_match:
            slug = dir_match.group(1)
            anchor = dir_match.group(2) or ""
            return f"[{link_text}]({slug}.md{anchor})"

        docs_workflows_match = re.fullmatch(
            r"\.\./\.\./docs/workflows/([a-z0-9-]+)\.md(#.*)?", target
        )
        if docs_workflows_match:
            slug = docs_workflows_match.group(1)
            anchor = docs_workflows_match.group(2) or ""
            return f"[{link_text}](../{slug}.md{anchor})"

        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, readme)


def _generate_page(workflow_dir: Path) -> str:
    readme = (workflow_dir / "README.md").read_text(encoding="utf-8")
    example = (workflow_dir / "example.yml").read_text(encoding="utf-8")

    # Remove "See [example.yml](example.yml) for the full workflow file." since
    # the example is shown inline in the section below.  The leading \n is
    # consumed so we don't leave a blank line; the trailing newline (if any) is
    # left in place.
    readme = re.sub(
        r"\nSee \[example\.yml\]\(example\.yml\)[^\n]*",
        "",
        readme,
    )

    # Rewrite sibling-workflow links so they resolve on the docs site.
    # In the source tree READMEs use ../other-workflow/README.md or
    # ../other-workflow/ to link to neighbours; on the generated docs site the
    # correct target is other-workflow.md (a peer file in the same directory).
    readme = _rewrite_sibling_workflow_links(readme)

    # Insert a "Workflow source" link after the first paragraph (the short
    # description that follows the H1 title) so readers can easily navigate
    # to the prompt source.
    source_link = _workflow_source_link(example)
    if source_link:
        readme = re.sub(
            r"(^# [^\n]+\n\n)([^\n]+\n)",
            rf"\1\2\n**Workflow source:** {source_link}\n",
            readme,
            count=1,
            flags=re.MULTILINE,
        )

    return f"{readme.rstrip()}\n\n## Example Workflow\n\n```yaml\n{example.rstrip()}\n```\n"


def on_pre_build(config):
    """Create a fresh temp directory for generated pages before each build."""
    global _tmp_dir
    if _tmp_dir is not None:
        shutil.rmtree(_tmp_dir, ignore_errors=True)
    _tmp_dir = tempfile.mkdtemp(prefix="mkdocs_gh_agent_")
    atexit.register(shutil.rmtree, _tmp_dir, True)


def on_files(files, config):
    repo_root = Path(config["docs_dir"]).parent
    workflows_path = repo_root / _WORKFLOWS_DIR

    for workflow_dir in sorted(workflows_path.iterdir()):
        readme_path = workflow_dir / "README.md"
        example_path = workflow_dir / "example.yml"
        if not (workflow_dir.is_dir() and readme_path.exists() and example_path.exists()):
            continue

        page_content = _generate_page(workflow_dir)
        rel_path = f"{_DOCS_DEST}/{workflow_dir.name}.md"

        tmp_file = Path(_tmp_dir) / rel_path
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file.write_text(page_content, encoding="utf-8")

        files.append(
            File(
                path=rel_path,
                src_dir=_tmp_dir,
                dest_dir=config["site_dir"],
                use_directory_urls=config.get("use_directory_urls", True),
            )
        )

    return files
