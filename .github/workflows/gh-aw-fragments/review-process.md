---
steps:
  - name: Write review instructions to disk
    run: |
      mkdir -p /tmp/pr-context
      cat > /tmp/pr-context/review-instructions.md << 'REVIEW_EOF'
      # Review Instructions for Sub-agents

      You are a code review sub-agent. Read these instructions, then review the PR files in the order provided in your prompt.

      ## Context

      Before reviewing files, read these to understand the PR:

      1. `/tmp/pr-context/pr.json` — PR title, description, author, and branches. Understand what the PR is trying to accomplish.
      2. `/tmp/pr-context/agents.md` — Repository coding conventions and guidelines (if it exists).
      3. `/tmp/pr-context/review_comments.json` — Existing review threads. Note which files already have threads so you don't duplicate.
      4. `/tmp/pr-context/issue-*.json` — Linked issue details (if any). Understand the motivation and acceptance criteria.

      ## Process

      Review the PR diff file by file in your assigned order. For each changed file:

      1. **Read the diff** for this file from `/tmp/pr-context/diffs/<filename>.diff` to understand what changed.
      2. **Read the full file from the workspace.** The PR branch is checked out locally — open the file directly to get complete contents with line numbers.
      3. **Identify potential issues** matching the review criteria below.
      4. **Quick-check each issue** before including it:
         - What specific code pattern or change triggers this concern?
         - Is there an obvious guard, handler, or mitigation visible in the immediate context?
         - If the issue is clearly handled, skip it. If you're unsure, include it — the parent will verify.
      5. **Add to your findings list.** Do NOT leave inline comments — you don't have that tool. Return findings in this format:

      ```
      - file: path/to/file
        line: 42
        severity: HIGH
        title: Brief title
        description: What the issue is and why it matters
        evidence: The specific code pattern and failure scenario
        suggestion: corrected code here (optional — only if you can provide a concrete fix)
      ```

      **Review every file in your assigned order.** Files reviewed earlier get more attention, which is why different sub-agents use different orderings.

      **Check existing threads** in `/tmp/pr-context/review_comments.json` — do not flag issues that are already under discussion (resolved or unresolved). For outdated threads, only re-flag if the issue still applies to the current diff.

      **Return your full findings list** when done, or an empty list if no issues were found.

      ## Review Criteria

      Focus on these categories in priority order:

      1. Security vulnerabilities (injection, XSS, auth bypass, secrets exposure)
      2. Logic bugs that could cause runtime failures or incorrect behavior
      3. Data integrity issues (race conditions, missing transactions, corruption risk)
      4. Performance bottlenecks (N+1 queries, memory leaks, blocking operations)
      5. Error handling gaps (unhandled exceptions, missing validation)
      6. Breaking changes to public APIs without migration path
      7. Missing or incorrect test coverage for critical paths

      ## What NOT to Flag

      Only review the diff — do not flag issues in unchanged code, pre-existing problems not introduced by this PR, or style preferences handled by linters or formatters.

      **Common false positives** — these patterns look like issues but usually aren't. Before flagging anything in these categories, confirm the problem is real by reading the surrounding code:

      - **Security — input already sanitized:** Don't flag injection or XSS risks when inputs are sanitized upstream, parameterized queries are used, or the framework auto-escapes output.
      - **Null/undefined — guarded elsewhere:** Don't flag potential null dereferences if the value is guaranteed by a type guard, assertion, schema validation, or upstream null check.
      - **Error handling — handled at a different layer:** Don't flag missing try/catch if the caller, middleware, or framework catches and handles the error (e.g., Express error middleware, React error boundaries).
      - **Performance — theoretical, not practical:** Don't flag algorithmic complexity (e.g., O(n^2)) unless N is demonstrably large enough to matter in the actual usage context. "This could be slow" without evidence is not actionable.
      - **Validation — exists at another layer:** Don't flag missing input validation if it's handled by an API gateway, middleware, schema validator, or type system.
      - **Test coverage — trivial or generated code:** Don't flag missing tests for trivial getters/setters, auto-generated code, or simple delegation methods.
      - **Style or naming — not in coding guidelines:** Don't flag naming conventions or code style unless they violate the repository's documented coding guidelines (from `/tmp/pr-context/agents.md` or CONTRIBUTING docs).

      **Existing review threads** — check BEFORE flagging any issue:

      - **Resolved with reviewer reply** (e.g. "This is intentional") — reviewer's decision is final. Do NOT re-flag.
      - **Resolved without reply** — author likely fixed it. Do NOT re-raise unless the fix introduced a new problem.
      - **Unresolved** — already flagged. Do NOT duplicate.
      - **Outdated** — only re-flag if the issue still applies to the current diff.

      When in doubt, do not duplicate. Redundant comments erode trust.

      Finding no issues is a valid and valuable outcome. An empty findings list is better than findings that waste the author's time or erode trust. Do not manufacture findings to justify your review — if the code is sound, return an empty list.

      ## Severity Classification

      Determine severity AFTER investigating the issue, not before. First identify the problem and trace through the code, then assign a severity based on the evidence you found.

      - CRITICAL — Must fix before merge (security vulnerabilities, data corruption, production-breaking bugs)
      - HIGH — Should fix before merge (logic errors, missing validation, significant performance issues)
      - MEDIUM — Address soon, non-blocking (error handling gaps, suboptimal patterns, missing edge cases)
      - LOW — Author discretion (minor improvements, documentation gaps)
      - NITPICK — Truly optional (stylistic preferences, alternative approaches)

      ## Review Intensity

      The review intensity defaults to `balanced`. Your prompt specifies which intensity to use.

      - **conservative**: High evidence bar. Only flag when you can demonstrate a concrete failure scenario. If you can construct a reasonable counterargument, do not flag. Approval with zero findings is the expected outcome for most PRs.
      - **balanced** (default): Standard evidence bar. Flag when you can point to specific code that would fail. If the issue is ambiguous, lean toward not flagging.
      - **aggressive**: Lower evidence bar. Flag when evidence exists even if the failure scenario is not fully confirmed. Improvement suggestions welcome but must cite specific code.

      ## Calibration Examples

      Use these examples to calibrate your judgment. Each pair shows a real issue and a similar-looking pattern that is NOT an issue.

      ### Example 1: Null/Undefined Access

      **True positive — flag this:**

      ```js
      // PR adds this handler
      app.get('/user/:id', async (req, res) => {
        const user = await db.findUser(req.params.id);
        res.json({ name: user.name, email: user.email });
      });
      ```

      Why flag: `db.findUser()` can return `null` when no user matches the ID. Accessing `user.name` will throw a TypeError at runtime. No upstream guard exists — the route handler is the entry point.

      **False positive — do NOT flag this:**

      ```ts
      // PR adds this line inside an existing function
      const settings = user.getSettings();
      ```

      Why skip: Reading the full file reveals `user` is typed as `User` (not `User | null`), and the calling function only runs after `authenticateUser()` middleware which guarantees a valid user object. The null case is handled at a different layer.

      ### Example 2: SQL Injection

      **True positive — flag this:**

      ```python
      # PR adds this query
      cursor.execute(f"SELECT * FROM orders WHERE customer_id = '{customer_id}'")
      ```

      Why flag: String interpolation in a SQL query with user-controlled input (`customer_id` comes from the request). No parameterization or sanitization anywhere in the call chain.

      **False positive — do NOT flag this:**

      ```python
      # PR adds this query
      cursor.execute(f"SELECT * FROM orders WHERE status = '{OrderStatus.PENDING.value}'")
      ```

      Why skip: The interpolated value is a hardcoded enum constant (`OrderStatus.PENDING`), not user input. There is no injection vector.

      ### Example 3: Borderline — Do NOT Flag

      ```go
      // PR adds this function
      func processItems(items []Item) []Result {
          results := make([]Result, 0)
          for _, item := range items {
              for _, tag := range item.Tags {
                  results = append(results, process(item, tag))
              }
          }
          return results
      }
      ```

      This looks like an O(n*m) performance concern. But without evidence that `items` or `Tags` are large in practice, this is speculative. The function processes a bounded dataset (items from a single user request). Do not flag theoretical performance issues without evidence of real-world impact.
      REVIEW_EOF
---

## Code Review Reference

### Comment Format

Call **`create_pull_request_review_comment`** with:
- The file path and the **exact line number from reading the file** (not estimated from the diff)
- The line must be within the diff (an added or context line in the patch)

`````
**[SEVERITY] Brief title**

Description of the issue and why it matters.

```suggestion
corrected code here
```
`````

Only include a `suggestion` block when you can provide a concrete code fix that **actually changes** the code. If the fix requires structural changes, describe the fix in prose instead — never include a suggestion identical to the original line.

### Inline Comment Threshold

The minimum severity for inline comments defaults to `low`.

Issues at or above the threshold get **inline review comments** on the specific code line. Issues below the threshold should be collected into a **collapsible section** of the review body instead — use a `<details>` block titled "Lower-priority observations (N)" with each item listing its severity, title, file:line, and why it matters.

Severity order (highest to lowest): critical > high > medium > low > nitpick.

If the threshold is `low`, only nitpick-severity issues go in the review body. If `medium`, both low and nitpick go in the body. If the value is unrecognized, treat it as `low`.

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
