## Code Review Reference

### File-by-File Process

Fetch changed files with `pull_request_read` method `get_files` using `per_page: 5, page: 1`. Then review **one file at a time**:

**For each changed file:**

1. **Read the patch** to understand what changed.
2. **Read the full file from the workspace.** The PR branch is checked out locally — open the file directly to get complete contents with line numbers. This lets you understand context, verify issues aren't handled elsewhere, and determine exact line numbers.
3. **Identify issues** matching the review criteria below.
4. **Thoroughly investigate** — trace the code path to confirm the problem would actually occur at runtime and that the issue is not a false positive.
5. **Leave inline comments NOW** — call `create_pull_request_review_comment` for every issue in this file before moving on. Do not batch comments across files.

**Repeat for the next file.** After all files in the page, fetch `page: 2` and continue until all changed files are reviewed.

**IMPORTANT:** Do not read all files first and comment later. Review and comment on each file before starting the next one. This ensures comments are grounded in the file you just read.

### Comment Format

Call **`create_pull_request_review_comment`** with:
- The file path and the **exact line number from reading the file** (not estimated from the patch)
- The line must be within the diff (an added or context line in the patch)

`````
**[SEVERITY] Brief title**

Description of the issue and why it matters.

```suggestion
corrected code here
```
`````

Only include a `suggestion` block when you can provide a concrete code fix that **actually changes** the code. If the fix requires structural changes, describe the fix in prose instead — never include a suggestion identical to the original line.

### What NOT to Flag

- Issues in unchanged code (only review the diff)
- Style preferences handled by linters or formatters
- Pre-existing issues not introduced by this PR
- Issues already covered by existing review threads — see rules below

### Existing Thread Rules

Check BEFORE leaving any comment:

- **Resolved with reviewer reply** (e.g. "This is intentional") — reviewer's decision is final. Do NOT re-flag.
- **Resolved without reply** — author likely fixed it. Do NOT re-raise unless the fix introduced a new problem.
- **Unresolved** — already flagged. Do NOT duplicate.
- **Outdated** — only re-flag if the issue still applies to the current diff.

When in doubt, do not duplicate. Redundant comments erode trust.

**Before flagging any issue, verify it against the actual code.**

### Severity Classification

- 🔴 **CRITICAL** — Must fix before merge (security vulnerabilities, data corruption, production-breaking bugs)
- 🟠 **HIGH** — Should fix before merge (logic errors, missing validation, significant performance issues)
- 🟡 **MEDIUM** — Address soon, non-blocking (error handling gaps, suboptimal patterns, missing edge cases)
- ⚪ **LOW** — Author discretion (minor improvements, documentation gaps)
- 💬 **NITPICK** — Truly optional (stylistic preferences, alternative approaches)

### Review Criteria

Focus on these categories in priority order:

1. Security vulnerabilities (injection, XSS, auth bypass, secrets exposure)
2. Logic bugs that could cause runtime failures or incorrect behavior
3. Data integrity issues (race conditions, missing transactions, corruption risk)
4. Performance bottlenecks (N+1 queries, memory leaks, blocking operations)
5. Error handling gaps (unhandled exceptions, missing validation)
6. Breaking changes to public APIs without migration path
7. Missing or incorrect test coverage for critical paths
