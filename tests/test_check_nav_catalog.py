"""Tests for scripts/check-nav-catalog.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "check-nav-catalog.py"
SPEC = importlib.util.spec_from_file_location("check_nav_catalog", MODULE_PATH)
assert SPEC and SPEC.loader
check_nav_catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_nav_catalog)


def test_extract_catalog_slugs_handles_anchor_query_and_invalid_cases() -> None:
    catalog = """
- [A](gh-agent-workflows/bug-hunter.md)
- [B](gh-agent-workflows/create-pr-from-issue.md#usage)
- [C](gh-agent-workflows/review-pr.md?tab=readme)
- [Invalid uppercase](gh-agent-workflows/Bad-Workflow.md)
- [Invalid ext](gh-agent-workflows/not-a-workflow.txt)
"""

    assert check_nav_catalog.extract_catalog_slugs(catalog) == {
        "bug-hunter",
        "create-pr-from-issue",
        "review-pr",
    }


def test_extract_catalog_slugs_ignores_links_inside_html_comments() -> None:
    catalog = """
<!--
- [Hidden](gh-agent-workflows/hidden-workflow.md)
-->
- [Visible](gh-agent-workflows/visible-workflow.md)
"""

    assert check_nav_catalog.extract_catalog_slugs(catalog) == {"visible-workflow"}


def test_extract_nav_slugs_stays_within_nav_block() -> None:
    mkdocs = """
site_name: docs
nav:
  - Home: index.md
  - Workflows:
      - Bug Hunter: workflows/gh-agent-workflows/bug-hunter.md
      - Create PR: workflows/gh-agent-workflows/create-pr-from-issue.md

plugins:
  - search
# Mention after nav should not be parsed:
extra: workflows/gh-agent-workflows/outside-nav.md
"""

    assert check_nav_catalog.extract_nav_slugs(mkdocs) == {
        "bug-hunter",
        "create-pr-from-issue",
    }


def test_extract_nav_slugs_ignores_commented_nav_entries() -> None:
    mkdocs = """
site_name: docs
nav:
  - Home: index.md
  # - Bug Hunter: workflows/gh-agent-workflows/bug-hunter.md
  - Workflows:
      - Create PR: workflows/gh-agent-workflows/create-pr-from-issue.md
"""

    assert check_nav_catalog.extract_nav_slugs(mkdocs) == {"create-pr-from-issue"}


def test_extract_mentioned_slugs_from_links_and_directory_references() -> None:
    page = """
See [Bug Hunter](gh-agent-workflows/bug-hunter.md#details) and
[Create PR](gh-agent-workflows/create-pr-from-issue.md?tab=readme).
Template path: gh-agent-workflows/review-pr/example.yml
"""

    assert check_nav_catalog.extract_mentioned_slugs(page) == {
        "bug-hunter",
        "create-pr-from-issue",
        "review-pr",
    }


def test_extract_mentioned_slugs_ignores_html_comments() -> None:
    page = """
<!--
Mentioned only in comment:
gh-agent-workflows/ghost-workflow.md
gh-agent-workflows/another-ghost/
-->
Visible mention: gh-agent-workflows/bug-hunter.md
"""

    assert check_nav_catalog.extract_mentioned_slugs(page) == {"bug-hunter"}


def test_covered_slugs_includes_transitive_mentions(tmp_path: Path, monkeypatch) -> None:
    docs_dir = tmp_path / "docs" / "workflows" / "gh-agent-workflows"
    docs_dir.mkdir(parents=True)
    (docs_dir / "overview.md").write_text(
        "See gh-agent-workflows/bug-hunter.md and gh-agent-workflows/review-pr/", encoding="utf-8"
    )

    monkeypatch.setattr(check_nav_catalog, "STATIC_DOCS_DIR", docs_dir)

    result = check_nav_catalog.covered_slugs({"overview"})
    assert result == {"overview", "bug-hunter", "review-pr"}


def test_main_returns_success_when_catalog_is_reachable(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    mkdocs = tmp_path / "mkdocs.yml"
    catalog = tmp_path / "catalog.md"
    docs_dir = tmp_path / "docs" / "workflows" / "gh-agent-workflows"
    docs_dir.mkdir(parents=True)

    mkdocs.write_text(
        """
nav:
  - Workflows:
      - Overview: workflows/gh-agent-workflows/overview.md
""",
        encoding="utf-8",
    )

    (docs_dir / "overview.md").write_text(
        "Covers gh-agent-workflows/bug-hunter.md", encoding="utf-8"
    )

    catalog.write_text("- [Bug Hunter](gh-agent-workflows/bug-hunter.md)\n", encoding="utf-8")

    monkeypatch.setattr(check_nav_catalog, "MKDOCS_YML", mkdocs)
    monkeypatch.setattr(check_nav_catalog, "CATALOG_MD", catalog)
    monkeypatch.setattr(check_nav_catalog, "STATIC_DOCS_DIR", docs_dir)

    rc = check_nav_catalog.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "OK: all 1 catalog workflows are reachable from nav" in out


def test_main_reports_missing_slugs_and_nonzero_exit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    mkdocs = tmp_path / "mkdocs.yml"
    catalog = tmp_path / "catalog.md"
    docs_dir = tmp_path / "docs" / "workflows" / "gh-agent-workflows"
    docs_dir.mkdir(parents=True)

    mkdocs.write_text(
        """
nav:
  - Workflows:
      - Bug Hunter: workflows/gh-agent-workflows/bug-hunter.md
""",
        encoding="utf-8",
    )

    catalog.write_text(
        """
- [Bug Hunter](gh-agent-workflows/bug-hunter.md)
- [Create PR](gh-agent-workflows/create-pr-from-issue.md)
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(check_nav_catalog, "MKDOCS_YML", mkdocs)
    monkeypatch.setattr(check_nav_catalog, "CATALOG_MD", catalog)
    monkeypatch.setattr(check_nav_catalog, "STATIC_DOCS_DIR", docs_dir)

    rc = check_nav_catalog.main()
    out = capsys.readouterr().out

    assert rc == 1
    assert "not reachable from mkdocs.yml nav" in out
    assert "- create-pr-from-issue" in out


def test_main_ignores_catalog_links_inside_html_comments(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    mkdocs = tmp_path / "mkdocs.yml"
    catalog = tmp_path / "catalog.md"
    docs_dir = tmp_path / "docs" / "workflows" / "gh-agent-workflows"
    docs_dir.mkdir(parents=True)

    mkdocs.write_text(
        """
nav:
  - Workflows:
      - Visible Workflow: workflows/gh-agent-workflows/visible-workflow.md
""",
        encoding="utf-8",
    )

    catalog.write_text(
        """
<!--
- [Hidden Workflow](gh-agent-workflows/hidden-workflow.md)
-->
- [Visible Workflow](gh-agent-workflows/visible-workflow.md)
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(check_nav_catalog, "MKDOCS_YML", mkdocs)
    monkeypatch.setattr(check_nav_catalog, "CATALOG_MD", catalog)
    monkeypatch.setattr(check_nav_catalog, "STATIC_DOCS_DIR", docs_dir)

    rc = check_nav_catalog.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "OK: all 1 catalog workflows are reachable from nav" in out
