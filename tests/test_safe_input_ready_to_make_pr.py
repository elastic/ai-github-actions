"""Tests for the ready-to-make-pr safe-input Python scripts.

Extracts the `py:` blocks from safe-output-push-to-pr.md and
safe-output-create-pr.md, runs them in controlled git environments,
and validates the JSON output and side effects.
"""

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest
import yaml

FRAGMENTS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".github"
    / "workflows"
    / "gh-aw-fragments"
)

PUSH_FRAGMENT = FRAGMENTS_DIR / "safe-output-push-to-pr.md"
CREATE_FRAGMENT = FRAGMENTS_DIR / "safe-output-create-pr.md"


def extract_py_block(fragment_path: Path) -> str:
    """Extract the py: block from a safe-input fragment's YAML frontmatter."""
    text = fragment_path.read_text()
    # Strip leading/trailing --- to get YAML frontmatter
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"Expected YAML frontmatter in {fragment_path}"
    frontmatter = yaml.safe_load(parts[1])
    py_code = frontmatter["safe-inputs"]["ready-to-make-pr"]["py"]
    assert py_code, f"No py: block found in {fragment_path}"
    return py_code


def run_py_in_repo(py_code: str, repo_dir: str) -> dict:
    """Run extracted Python code in a git repo and return parsed JSON output."""
    result = subprocess.run(
        ["python3", "-c", py_code],
        capture_output=True,
        text=True,
        cwd=repo_dir,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Script failed (rc={result.returncode}):\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    output = result.stdout.strip()
    assert output, "Script produced no output"
    return json.loads(output)


def make_git_repo(tmp_path: Path, *, with_upstream: bool = False) -> Path:
    """Create a minimal git repo. Optionally set up a remote upstream."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        subprocess.run(
            ["git"] + list(args),
            cwd=str(repo),
            capture_output=True,
            check=True,
        )

    git("init", "-b", "main")
    git("config", "user.email", "test@test.com")
    git("config", "user.name", "Test")

    # Initial commit
    (repo / "file.txt").write_text("hello\n")
    git("add", "file.txt")
    git("commit", "-m", "init")

    if with_upstream:
        # Create a bare remote and push
        remote = tmp_path / "remote.git"
        subprocess.run(
            ["git", "clone", "--bare", str(repo), str(remote)],
            capture_output=True,
            check=True,
        )
        git("remote", "add", "origin", str(remote))
        git("fetch", "origin")
        git("branch", "--set-upstream-to", "origin/main", "main")

    return repo


# ---------------------------------------------------------------------------
# Extraction tests
# ---------------------------------------------------------------------------


class TestExtraction:
    """Verify we can extract valid Python from both fragments."""

    def test_push_fragment_exists(self):
        assert PUSH_FRAGMENT.exists()

    def test_create_fragment_exists(self):
        assert CREATE_FRAGMENT.exists()

    def test_push_extract(self):
        code = extract_py_block(PUSH_FRAGMENT)
        assert "import" in code
        assert "json.dumps" in code

    def test_create_extract(self):
        code = extract_py_block(CREATE_FRAGMENT)
        assert "import" in code
        assert "json.dumps" in code

    def test_fragments_have_identical_py(self):
        """The two fragments should have identical Python logic."""
        push_code = extract_py_block(PUSH_FRAGMENT)
        create_code = extract_py_block(CREATE_FRAGMENT)
        assert push_code == create_code


# ---------------------------------------------------------------------------
# Output schema tests
# ---------------------------------------------------------------------------


class TestOutputSchema:
    """Validate JSON output structure across scenarios."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(PUSH_FRAGMENT)

    def test_basic_output_fields(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        output = run_py_in_repo(py_code, str(repo))

        assert output["status"] == "ok"
        assert isinstance(output["checklist"], list)
        assert isinstance(output["diff_line_count"], int)
        assert "contributing_guide" in output
        assert "pr_template" in output

    def test_checklist_always_has_validation_item(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        output = run_py_in_repo(py_code, str(repo))

        checklist_text = " ".join(output["checklist"])
        assert "fully completed and validated" in checklist_text


# ---------------------------------------------------------------------------
# Git diff fallback tests
# ---------------------------------------------------------------------------


class TestDiffFallbacks:
    """Test the 3-step diff fallback chain."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(PUSH_FRAGMENT)

    def test_with_upstream_uncommitted_changes(self, py_code, tmp_path):
        """--merge-base @{upstream} should capture uncommitted changes."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "file.txt").write_text("hello\nworld\n")

        output = run_py_in_repo(py_code, str(repo))
        assert output["diff_line_count"] > 0

        diff_file = Path("/tmp/self-review/diff.patch")
        assert diff_file.exists()
        assert "world" in diff_file.read_text()

    def test_with_upstream_committed_changes(self, py_code, tmp_path):
        """--merge-base @{upstream} should capture committed unpushed changes."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "new_file.txt").write_text("new content\n")
        subprocess.run(
            ["git", "add", "new_file.txt"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "add new file"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )

        output = run_py_in_repo(py_code, str(repo))
        assert output["diff_line_count"] > 0
        assert "new content" in Path("/tmp/self-review/diff.patch").read_text()

    def test_no_upstream_uncommitted_changes(self, py_code, tmp_path):
        """Falls back to git diff HEAD when no upstream is configured."""
        repo = make_git_repo(tmp_path, with_upstream=False)
        (repo / "file.txt").write_text("hello\nchanged\n")

        output = run_py_in_repo(py_code, str(repo))
        assert output["diff_line_count"] > 0
        assert "changed" in Path("/tmp/self-review/diff.patch").read_text()

    def test_no_upstream_committed_changes(self, py_code, tmp_path):
        """Falls back through chain; git diff @{upstream} (2-dot) also fails,
        git diff HEAD shows nothing since changes are committed. diff_line_count is 0."""
        repo = make_git_repo(tmp_path, with_upstream=False)
        (repo / "extra.txt").write_text("extra\n")
        subprocess.run(
            ["git", "add", "extra.txt"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "add extra"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )

        output = run_py_in_repo(py_code, str(repo))
        # No upstream and no uncommitted changes — diff is empty
        assert output["diff_line_count"] == 0

    def test_no_changes_at_all(self, py_code, tmp_path):
        """No changes yields empty diff and no self-review checklist item."""
        repo = make_git_repo(tmp_path, with_upstream=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["diff_line_count"] == 0

        checklist_text = " ".join(output["checklist"])
        assert "self-review" not in checklist_text


# ---------------------------------------------------------------------------
# File output tests
# ---------------------------------------------------------------------------


class TestFileOutput:
    """Verify files are created with expected content."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(PUSH_FRAGMENT)

    def test_diff_patch_created(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "file.txt").write_text("modified\n")

        run_py_in_repo(py_code, str(repo))

        assert Path("/tmp/self-review/diff.patch").exists()
        assert Path("/tmp/self-review/stat.txt").exists()

    def test_stat_matches_diff(self, py_code, tmp_path):
        """stat.txt should reference the same files as the diff."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "file.txt").write_text("modified\n")

        run_py_in_repo(py_code, str(repo))

        stat = Path("/tmp/self-review/stat.txt").read_text()
        assert "file.txt" in stat

    def test_empty_diff_writes_empty_files(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)

        run_py_in_repo(py_code, str(repo))

        assert Path("/tmp/self-review/diff.patch").read_text() == ""
        assert Path("/tmp/self-review/stat.txt").read_text() == ""


# ---------------------------------------------------------------------------
# Contributing / PR template detection
# ---------------------------------------------------------------------------


class TestFileDetection:
    """Test detection of CONTRIBUTING.md and PR template files."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(PUSH_FRAGMENT)

    def test_finds_contributing(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "CONTRIBUTING.md").write_text("# Contributing\n")

        output = run_py_in_repo(py_code, str(repo))
        assert output["contributing_guide"] == "CONTRIBUTING.md"
        assert any("contributing guide" in c.lower() for c in output["checklist"])

    def test_finds_nested_contributing(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "docs").mkdir()
        (repo / "docs" / "CONTRIBUTING.md").write_text("# Contributing\n")

        output = run_py_in_repo(py_code, str(repo))
        assert output["contributing_guide"] == "docs/CONTRIBUTING.md"

    def test_no_contributing(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["contributing_guide"] is None
        assert not any("contributing guide" in c.lower() for c in output["checklist"])

    def test_finds_pr_template(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / ".github").mkdir()
        (repo / ".github" / "pull_request_template.md").write_text("## PR\n")

        output = run_py_in_repo(py_code, str(repo))
        assert output["pr_template"] == ".github/pull_request_template.md"

    def test_no_pr_template(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["pr_template"] is None


# ---------------------------------------------------------------------------
# Self-review checklist gating
# ---------------------------------------------------------------------------


class TestSelfReviewGating:
    """The self-review checklist item should only appear when there's a diff."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(PUSH_FRAGMENT)

    def test_self_review_present_when_diff(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "file.txt").write_text("changed\n")

        output = run_py_in_repo(py_code, str(repo))
        checklist_text = " ".join(output["checklist"])
        assert "self-review" in checklist_text
        assert "diff.patch" in checklist_text

    def test_self_review_absent_when_no_diff(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)

        output = run_py_in_repo(py_code, str(repo))
        checklist_text = " ".join(output["checklist"])
        assert "self-review" not in checklist_text

    def test_diff_line_count_in_checklist(self, py_code, tmp_path):
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "file.txt").write_text("line1\nline2\nline3\n")

        output = run_py_in_repo(py_code, str(repo))
        count = output["diff_line_count"]
        assert count > 0
        # The line count should appear in the checklist text
        assert f"({count} lines)" in " ".join(output["checklist"])
