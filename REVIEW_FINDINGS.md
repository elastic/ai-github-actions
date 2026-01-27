# Comprehensive Review Findings

## Summary

This document outlines all issues found during the thorough review of workflows, READMEs, and examples.

## Critical Issues

### 1. Legacy/Duplicate Action Files

These files appear to be legacy duplicates that should either be removed or updated:

#### `workflows/mention-pr/action.yml`
- **Issue**: Duplicate of `workflows/mention-in-pr/action.yml`
- **Problems**:
  - References scripts at `${{ github.action_path }}/scripts/` but scripts are actually in `mention-in-pr/scripts/`
  - Contains incorrect MCP tool reference: `mcp__agents-md-generator` (should only be `mcp__agents-md-generator__generate_agents_md`)
  - Path in usage comment is `workflows/mention-pr@v1` instead of `workflows/mention-in-pr@v1`
- **Recommendation**: **DELETE** this file - `mention-in-pr` is the correct, maintained version

#### `workflows/pr-review-ro/action.yml`
- **Issue**: Duplicate of `workflows/pr-review/ro/action.yml`
- **Problems**:
  - Uses wrong environment variable: `PR_REVIEW_COMMENTS_FILE` instead of `PR_REVIEW_COMMENTS_DIR` (scripts expect `DIR`)
  - References scripts at `${{ github.action_path }}/scripts/` but scripts are actually in `pr-review/scripts/` (should use `../scripts`)
  - Missing `pr-remove-comment.sh` in allowed-tools (present in the correct version)
  - Contains incorrect MCP tool reference: `mcp__agents-md-generator` (should only be `mcp__agents-md-generator__generate_agents_md`)
  - Path in usage comment is `workflows/pr-review-ro@v1` instead of `workflows/pr-review/ro@v1`
- **Recommendation**: **DELETE** this file - `pr-review/ro` is the correct, maintained version

#### `workflows/issue-triage/action.yml`
- **Issue**: Duplicate of `workflows/issue-triage/ro/action.yml`
- **Problems**:
  - Missing `<allowed_tools>` section in the prompt (referenced but not included)
  - Contains incorrect MCP tool reference: `mcp__agents-md-generator` (should only be `mcp__agents-md-generator__generate_agents_md`)
  - Path in usage comment is `workflows/issue-triage@v1` instead of `workflows/issue-triage/ro@v1`
  - References `issue-triage-execute` in prompt which doesn't exist (should reference `issue-triage/rwx`)
- **Recommendation**: **DELETE** this file - `issue-triage/ro` is the correct, maintained version

### 2. MCP Tool Reference Issues

Several actions have incorrect MCP tool references:

**Files with incorrect `mcp__agents-md-generator` (without function name):**
- `workflows/mention-pr/action.yml` (line 35)
- `workflows/pr-review-ro/action.yml` (line 35)
- `workflows/issue-triage/action.yml` (line 34)

**Correct reference**: Should only be `mcp__agents-md-generator__generate_agents_md`

**Note**: The correct version (`mcp__agents-md-generator__generate_agents_md`) is already present in these files, so the incorrect one should be removed.

### 3. Environment Variable Inconsistency

**File**: `workflows/pr-review-ro/action.yml` (line 72)
- Uses: `PR_REVIEW_COMMENTS_FILE: /tmp/pr-review-comments.json`
- Should be: `PR_REVIEW_COMMENTS_DIR: /tmp/pr-review-comments`
- Scripts (`pr-comment.sh`, `pr-review.sh`, `pr-remove-comment.sh`) all expect `PR_REVIEW_COMMENTS_DIR`

## Minor Issues / Observations

### 4. Script Path References

All legacy files reference scripts that don't exist in their directories:
- `mention-pr/action.yml` → scripts are in `mention-in-pr/scripts/`
- `pr-review-ro/action.yml` → scripts are in `pr-review/scripts/`

### 5. Missing Documentation

The main `README.md` doesn't mention the legacy/duplicate paths, which could confuse users.

### 6. Consistency Check: All Active Workflows

✅ **Verified**: All active workflows (`workflows/*/action.yml` and `workflows/*/ro/action.yml`, `workflows/*/rwx/action.yml`) have:
- Correct MCP tool references
- Proper environment variables
- Correct script paths
- Complete `<allowed_tools>` sections
- Matching READMEs and examples

## Recommendations

### Immediate Actions

1. **Delete legacy files**:
   - `workflows/mention-pr/action.yml`
   - `workflows/pr-review-ro/action.yml`
   - `workflows/issue-triage/action.yml`

2. **Verify no references** to these legacy paths exist in:
   - Documentation
   - Example workflows
   - Other repositories using these actions

### Verification Checklist

- [x] All active workflows reviewed
- [x] All READMEs match their action.yml files
- [x] All examples use correct paths
- [x] Script paths verified
- [x] Environment variables consistent
- [x] MCP tool references correct (in active files)
- [x] Prompt sections complete
- [x] Footer formats consistent

## Positive Findings

✅ **Excellent organization**: Clear separation between `ro` and `rwx` variants
✅ **Consistent patterns**: All workflows follow the same structure
✅ **Good documentation**: READMEs are comprehensive and match implementations
✅ **Proper tool restrictions**: Clear documentation of capabilities vs constraints
✅ **Script organization**: Shared scripts properly organized in `pr-review/scripts/`
✅ **MCP configuration**: Proper default MCP servers in workflow actions
✅ **Example workflows**: All examples are correct and usable

## Files Reviewed

### Active Workflows (All Good ✅)
- `base/action.yml`
- `workflows/build-failure-buildkite/` (action.yml, README.md, example.yml)
- `workflows/build-failure-github-actions/` (action.yml, README.md, example.yml)
- `workflows/feedback-summary/` (action.yml, README.md, example.yml)
- `workflows/issue-triage/ro/` (action.yml, README.md, example.yml)
- `workflows/issue-triage/rwx/` (action.yml, README.md, example.yml)
- `workflows/mention-in-issue/` (action.yml, README.md, example.yml)
- `workflows/mention-in-pr/` (action.yml, README.md, example.yml)
- `workflows/pr-review/ro/` (action.yml, README.md, example.yml)
- `workflows/pr-review/rwx/` (action.yml, README.md, example.yml)
- `workflows/project-manager/` (action.yml, README.md, example.yml)

### Legacy Files (Should be Deleted ❌)
- `workflows/mention-pr/action.yml`
- `workflows/pr-review-ro/action.yml`
- `workflows/issue-triage/action.yml`

### Supporting Files (All Good ✅)
- `README.md`
- `DEVELOPING.md`
- `CODE_STYLE.md`
- `Makefile`
- `.github/workflows/ci.yml`
- `compile.py`
- All scripts in `workflows/*/scripts/`
