from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_hooks_module():
    hooks_path = Path(__file__).resolve().parent.parent / "docs" / "hooks.py"
    spec = spec_from_file_location("docs_hooks", hooks_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_workflow_dir(tmp_path: Path, readme: str, example: str) -> Path:
    workflow_dir = tmp_path / "workflow"
    workflow_dir.mkdir()
    (workflow_dir / "README.md").write_text(readme, encoding="utf-8")
    (workflow_dir / "example.yml").write_text(example, encoding="utf-8")
    return workflow_dir


def test_generate_page_rewrites_sibling_workflow_readme_link(tmp_path):
    hooks = _load_hooks_module()
    workflow_dir = _create_workflow_dir(
        tmp_path,
        "# Workflow\n\nSee [Sibling](../other-workflow/README.md).\n",
        "name: test\njobs: {}\n",
    )

    page = hooks._generate_page(workflow_dir)

    assert "[Sibling](other-workflow.md)" in page
    assert "../other-workflow/README.md" not in page


def test_generate_page_rewrites_sibling_workflow_directory_link_with_anchor(tmp_path):
    hooks = _load_hooks_module()
    workflow_dir = _create_workflow_dir(
        tmp_path,
        "# Workflow\n\nSee [Sibling](../other-workflow/#details).\n",
        "name: test\njobs: {}\n",
    )

    page = hooks._generate_page(workflow_dir)

    assert "[Sibling](other-workflow.md#details)" in page
    assert "../other-workflow/#details" not in page


def test_generate_page_preserves_non_sibling_docs_links(tmp_path):
    hooks = _load_hooks_module()
    workflow_dir = _create_workflow_dir(
        tmp_path,
        "# Workflow\n\nSee [Detector / Fixer chaining](../../docs/workflows/detector-fixer-chaining.md).\n",
        "name: test\njobs: {}\n",
    )

    page = hooks._generate_page(workflow_dir)

    assert "[Detector / Fixer chaining](../../docs/workflows/detector-fixer-chaining.md)" in page
    assert "../docs.mdworkflows/detector-fixer-chaining.md" not in page
