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
    safe_inputs = frontmatter["safe-inputs"]
    # The safe-input key varies: ready-to-push-to-pr (push) vs ready-to-make-pr (create)
    first_key = next(iter(safe_inputs))
    py_code = safe_inputs[first_key]["py"]
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

    def test_fragments_share_common_structure(self):
        """Both fragments should share the same diff/checklist structure."""
        push_code = extract_py_block(PUSH_FRAGMENT)
        create_code = extract_py_block(CREATE_FRAGMENT)
        # Both should contain the core logic markers
        for marker in ["contributing = find(", "diff_line_count", "json.dumps", "self-review"]:
            assert marker in push_code, f"Push fragment missing '{marker}'"
            assert marker in create_code, f"Create fragment missing '{marker}'"


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

    def test_commits_txt_created(self, py_code, tmp_path):
        """commits.txt should capture commit messages since upstream."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "new.txt").write_text("new\n")
        subprocess.run(["git", "add", "new.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "add new feature"],
            cwd=str(repo), check=True, capture_output=True,
        )

        run_py_in_repo(py_code, str(repo))

        commits = Path("/tmp/self-review/commits.txt").read_text()
        assert "add new feature" in commits

    def test_readme_manifest_created(self, py_code, tmp_path):
        """README.md manifest should be created with review instructions."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "file.txt").write_text("modified\n")

        run_py_in_repo(py_code, str(repo))

        readme = Path("/tmp/self-review/README.md").read_text()
        assert "Self-Review Context" in readme
        assert "diff.patch" in readme
        assert "commits.txt" in readme
        assert "notes.md" in readme


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
        assert "README.md" in checklist_text

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


# ---------------------------------------------------------------------------
# Push fragment: history rewrite guard
# ---------------------------------------------------------------------------


def _get_head_sha(repo: Path) -> str:
    """Get the current HEAD commit SHA."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _write_pr_json(head_sha: str) -> None:
    """Write a minimal pr.json with the given headRefOid."""
    os.makedirs("/tmp/pr-context", exist_ok=True)
    with open("/tmp/pr-context/pr.json", "w") as f:
        json.dump({"headRefOid": head_sha}, f)


def _cleanup_pr_json() -> None:
    """Remove pr.json so it doesn't leak between tests."""
    try:
        os.remove("/tmp/pr-context/pr.json")
    except FileNotFoundError:
        pass


class TestPushGuards:
    """Test the ancestry guard in the push fragment."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(PUSH_FRAGMENT)

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        _cleanup_pr_json()

    def test_no_pr_json_passes(self, py_code, tmp_path):
        """Without pr.json the guard is skipped — should succeed."""
        _cleanup_pr_json()
        repo = make_git_repo(tmp_path, with_upstream=True)
        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "ok"

    def test_normal_commit_passes(self, py_code, tmp_path):
        """A regular commit on top of the PR head should pass."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        head_sha = _get_head_sha(repo)
        _write_pr_json(head_sha)

        # Add a normal commit
        (repo / "new.txt").write_text("new\n")
        subprocess.run(["git", "add", "new.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add new"], cwd=str(repo), check=True, capture_output=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "ok"

    def test_history_rewrite_detected(self, py_code, tmp_path):
        """If HEAD diverges from PR head (rebase), guard should error."""
        repo = make_git_repo(tmp_path, with_upstream=True)

        # Record the initial head
        initial_sha = _get_head_sha(repo)

        # Make a second commit, then record that as PR head
        (repo / "a.txt").write_text("a\n")
        subprocess.run(["git", "add", "a.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "second"], cwd=str(repo), check=True, capture_output=True)
        pr_head = _get_head_sha(repo)

        # Now reset back to initial — simulates a rebase that dropped the PR head
        subprocess.run(["git", "reset", "--hard", initial_sha], cwd=str(repo), check=True, capture_output=True)
        (repo / "b.txt").write_text("b\n")
        subprocess.run(["git", "add", "b.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "diverged"], cwd=str(repo), check=True, capture_output=True)

        _write_pr_json(pr_head)
        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "error"
        assert "History rewrite" in output["error"]

    def test_merge_commit_allowed(self, py_code, tmp_path):
        """A merge commit after the PR head should be allowed for push."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        pr_head = _get_head_sha(repo)
        _write_pr_json(pr_head)

        # Create a side branch and merge it — produces a merge commit
        subprocess.run(["git", "checkout", "-b", "side"], cwd=str(repo), check=True, capture_output=True)
        (repo / "side.txt").write_text("side\n")
        subprocess.run(["git", "add", "side.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "side"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=str(repo), check=True, capture_output=True)
        (repo / "main2.txt").write_text("main2\n")
        subprocess.run(["git", "add", "main2.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "main2"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "merge", "side", "--no-edit"], cwd=str(repo), check=True, capture_output=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "ok"


# ---------------------------------------------------------------------------
# Create fragment: merge commit guard
# ---------------------------------------------------------------------------


class TestCreateGuards:
    """Test guards in the create fragment (bundle format supports merge commits)."""

    @pytest.fixture
    def py_code(self):
        return extract_py_block(CREATE_FRAGMENT)

    def test_normal_commit_passes(self, py_code, tmp_path):
        """Regular commits should pass the create guard."""
        repo = make_git_repo(tmp_path, with_upstream=True)
        (repo / "new.txt").write_text("new\n")
        subprocess.run(["git", "add", "new.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add new"], cwd=str(repo), check=True, capture_output=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "ok"

    def test_merge_commit_allowed(self, py_code, tmp_path):
        """Merge commits are allowed with patch-format: bundle."""
        repo = make_git_repo(tmp_path, with_upstream=True)

        # Create a side branch and merge it
        subprocess.run(["git", "checkout", "-b", "side"], cwd=str(repo), check=True, capture_output=True)
        (repo / "side.txt").write_text("side\n")
        subprocess.run(["git", "add", "side.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "side"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=str(repo), check=True, capture_output=True)
        (repo / "main2.txt").write_text("main2\n")
        subprocess.run(["git", "add", "main2.txt"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "main2"], cwd=str(repo), check=True, capture_output=True)
        subprocess.run(["git", "merge", "side", "--no-edit"], cwd=str(repo), check=True, capture_output=True)

        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "ok"

    def test_no_upstream_fails_closed(self, py_code, tmp_path):
        """Without an upstream ref, the create guard should fail closed."""
        repo = make_git_repo(tmp_path, with_upstream=False)

        output = run_py_in_repo(py_code, str(repo))
        assert output["status"] == "error"
        assert "upstream" in output["error"].lower()
