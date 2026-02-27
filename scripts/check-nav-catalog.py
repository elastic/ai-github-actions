#!/usr/bin/env python3
"""Validate that mkdocs.yml nav entries cover all workflows listed in the catalog.

Each workflow slug referenced in the "Available workflows" catalog
(docs/workflows/gh-agent-workflows.md) must be reachable from the mkdocs.yml nav,
either:

  1. As a direct nav entry (workflows/gh-agent-workflows/<slug>.md), or
  2. Mentioned in the content of a static overview page that IS in the nav
     (e.g. docs/workflows/gh-agent-workflows/bugs.md covers bug-hunter and
     bug-exterminator via inline documentation).

Exits with a non-zero status and prints the missing slugs when drift is detected.

Elastic-specific workflows (prefix ``estc-``) live in their own nav section and
are excluded from this check.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
CATALOG_MD = REPO_ROOT / "docs" / "workflows" / "gh-agent-workflows.md"
STATIC_DOCS_DIR = REPO_ROOT / "docs" / "workflows" / "gh-agent-workflows"

ELASTIC_SPECIFIC_PREFIX = "estc-"


def extract_catalog_slugs(catalog_text: str) -> set[str]:
    """Extract workflow slugs from the markdown catalog page.

    Scans for Markdown link targets of the form::

        (gh-agent-workflows/<slug>.md)

    where ``<slug>`` is a lowercase alphanumeric-and-hyphen string.
    Returns the set of matching slugs.
    """
    return {
        m.group(1)
        for m in re.finditer(r"\(gh-agent-workflows/([a-z0-9-]+)\.md\)", catalog_text)
    }


def extract_nav_slugs(mkdocs_text: str) -> set[str]:
    """Extract workflow slugs directly referenced in the mkdocs.yml nav."""
    return {
        m.group(1)
        for m in re.finditer(
            r"workflows/gh-agent-workflows/([a-z0-9-]+)\.md", mkdocs_text
        )
    }


def extract_mentioned_slugs(page_content: str) -> set[str]:
    """Extract workflow slugs linked or referenced anywhere in a docs page.

    Detects two patterns:

    * Markdown link targets:   ``gh-agent-workflows/<slug>.md``
      (e.g. ``[Bug Hunter](gh-agent-workflows/bug-hunter.md)``)
    * Directory references:    ``gh-agent-workflows/<slug>/``
      (e.g. in curl install snippets: ``.../gh-agent-workflows/bug-hunter/example.yml``)
    """
    link_slugs = {
        m.group(1)
        for m in re.finditer(r"\bgh-agent-workflows/([a-z0-9-]+)\.md\b", page_content)
    }
    dir_slugs = {
        m.group(1)
        for m in re.finditer(r"\bgh-agent-workflows/([a-z0-9-]+)/", page_content)
    }
    return link_slugs | dir_slugs


def covered_slugs(nav_slugs: set[str]) -> set[str]:
    """Return the full set of workflow slugs reachable from the nav.

    Includes direct nav slugs plus any slugs mentioned in the content of static
    overview pages that are in the nav (e.g. bugs.md, code-duplication.md).
    """
    reachable = set(nav_slugs)

    for slug in nav_slugs:
        overview_path = STATIC_DOCS_DIR / f"{slug}.md"
        if overview_path.exists():
            content = overview_path.read_text(encoding="utf-8")
            reachable.update(extract_mentioned_slugs(content))

    return reachable


def main() -> int:
    catalog_text = CATALOG_MD.read_text(encoding="utf-8")
    mkdocs_text = MKDOCS_YML.read_text(encoding="utf-8")

    catalog_slugs = {
        s for s in extract_catalog_slugs(catalog_text)
        if not s.startswith(ELASTIC_SPECIFIC_PREFIX)
    }
    nav_slugs = {
        s for s in extract_nav_slugs(mkdocs_text)
        if not s.startswith(ELASTIC_SPECIFIC_PREFIX)
    }

    reachable = covered_slugs(nav_slugs)
    missing_from_nav = catalog_slugs - reachable

    if missing_from_nav:
        print(
            "ERROR: The following workflows are in the catalog "
            "but not reachable from mkdocs.yml nav:"
        )
        for slug in sorted(missing_from_nav):
            print(f"  - {slug}")
        return 1

    print(f"OK: all {len(catalog_slugs)} catalog workflows are reachable from nav")
    return 0


if __name__ == "__main__":
    sys.exit(main())
