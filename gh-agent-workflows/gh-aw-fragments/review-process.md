## Code Review Reference

### File-by-File Process

Fetch changed files with `pull_request_read` method `get_files` using `per_page: 5, page: 1`. Then review **one file at a time**:

**For each changed file:**

1. **Read the patch** to understand what changed.
2. **Read the full file from the workspace.** The PR branch is checked out locally — open the file directly to get complete contents with line numbers. This lets you understand context, verify issues aren't handled elsewhere, and determine exact line numbers.
3. **Identify issues** matching the review criteria below.
4. **Verify each issue** before commenting — work through these steps for every potential finding:
   1. What specific code pattern or change triggers this concern?
   2. Read the surrounding context — is this handled elsewhere in the file, caller, or framework?
   3. Construct a concrete failure scenario — what specific input or state causes the bug? If you cannot describe one, stop — do not flag.
   4. Challenge your own finding — would a senior engineer familiar with this codebase agree this is a real issue? If "probably not" or "unsure", stop — do not flag.
5. **Leave inline comments NOW** — call `create_pull_request_review_comment` for every verified issue in this file before moving on. Do not batch comments across files.

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

### Review Criteria

Focus on these categories in priority order:

1. Security vulnerabilities (injection, XSS, auth bypass, secrets exposure)
2. Logic bugs that could cause runtime failures or incorrect behavior
3. Data integrity issues (race conditions, missing transactions, corruption risk)
4. Performance bottlenecks (N+1 queries, memory leaks, blocking operations)
5. Error handling gaps (unhandled exceptions, missing validation)
6. Breaking changes to public APIs without migration path
7. Missing or incorrect test coverage for critical paths

### What NOT to Flag

Only review the diff — do not flag issues in unchanged code, pre-existing problems not introduced by this PR, or style preferences handled by linters or formatters.

**Common false positives** — these patterns look like issues but usually aren't. Before flagging anything in these categories, confirm the problem is real by reading the surrounding code:

- **Security — input already sanitized:** Don't flag injection or XSS risks when inputs are sanitized upstream, parameterized queries are used, or the framework auto-escapes output.
- **Null/undefined — guarded elsewhere:** Don't flag potential null dereferences if the value is guaranteed by a type guard, assertion, schema validation, or upstream null check.
- **Error handling — handled at a different layer:** Don't flag missing try/catch if the caller, middleware, or framework catches and handles the error (e.g., Express error middleware, React error boundaries).
- **Performance — theoretical, not practical:** Don't flag algorithmic complexity (e.g., O(n^2)) unless N is demonstrably large enough to matter in the actual usage context. "This could be slow" without evidence is not actionable.
- **Validation — exists at another layer:** Don't flag missing input validation if it's handled by an API gateway, middleware, schema validator, or type system.
- **Test coverage — trivial or generated code:** Don't flag missing tests for trivial getters/setters, auto-generated code, or simple delegation methods.
- **Style or naming — not in coding guidelines:** Don't flag naming conventions or code style unless they violate the repository's documented coding guidelines (from `generate_agents_md` or CONTRIBUTING docs).

**Existing review threads** — check BEFORE leaving any comment:

- **Resolved with reviewer reply** (e.g. "This is intentional") — reviewer's decision is final. Do NOT re-flag.
- **Resolved without reply** — author likely fixed it. Do NOT re-raise unless the fix introduced a new problem.
- **Unresolved** — already flagged. Do NOT duplicate.
- **Outdated** — only re-flag if the issue still applies to the current diff.

When in doubt, do not duplicate. Redundant comments erode trust.

Finding no issues is a valid and valuable outcome. An APPROVE with zero inline comments is better than comments that waste the author's time or erode trust. Do not manufacture findings to justify your review — if the code is sound, approve without comments.

### Severity Classification

Determine severity AFTER investigating the issue, not before. First identify the problem and trace through the code, then assign a severity based on the evidence you found. Do not start with a severity and look for issues to match it.

- 🔴 **CRITICAL** — Must fix before merge (security vulnerabilities, data corruption, production-breaking bugs)
- 🟠 **HIGH** — Should fix before merge (logic errors, missing validation, significant performance issues)
- 🟡 **MEDIUM** — Address soon, non-blocking (error handling gaps, suboptimal patterns, missing edge cases)
- ⚪ **LOW** — Author discretion (minor improvements, documentation gaps)
- 💬 **NITPICK** — Truly optional (stylistic preferences, alternative approaches)

### Review Intensity

The review intensity defaults to `balanced`.

- **`conservative`**: High evidence bar. Only comment when you can demonstrate a concrete failure scenario — what specific input or state triggers the bug. After identifying a potential issue, explicitly challenge your own finding: if you can construct a reasonable counterargument, do not comment. Give the author maximum benefit of the doubt. Approval with zero comments is the expected outcome for most PRs.
- **`balanced`** (default): Standard evidence bar. Comment when you can point to specific code that would fail and have verified the issue through the full verification protocol. Give the author reasonable benefit of the doubt — if the issue is ambiguous, lean toward not commenting.
- **`aggressive`**: Lower evidence bar. Comment when evidence exists even if the failure scenario is not fully confirmed. Improvement suggestions and alternative approaches are welcome but must still cite specific code. Do not speculate without any evidence, and do not duplicate existing threads.

If the value is unrecognized, treat it as `balanced`.

### Inline Comment Threshold

The minimum severity for inline comments defaults to `low`.

Issues at or above the threshold get **inline review comments** on the specific code line. Issues below the threshold should be collected into a **collapsible section** of the review body instead — use a `<details>` block titled "Lower-priority observations (N)" with each item listing its severity, title, file:line, and why it matters.

Severity order (highest to lowest): critical > high > medium > low > nitpick.

If the threshold is `low`, only nitpick-severity issues go in the review body. If `medium`, both low and nitpick go in the body. If the value is unrecognized, treat it as `low`.
