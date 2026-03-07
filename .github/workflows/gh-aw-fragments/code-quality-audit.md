Analyze the codebase for quality issues and file a structured report when concrete, actionable findings exist.

**The bar is high: only report issues backed by specific code evidence.** Most runs should end with `noop` — that means the code is in good shape for the dimension being audited. Filing nothing is a success when there is nothing worth filing.

### Severity Threshold: `${{ inputs.severity-threshold }}`

Only include findings at or above the configured severity:
- **high** — Correctness problems, user-facing defects, or violations of standards that directly impact users (e.g., WCAG failures that block keyboard users, race conditions that corrupt state, security vulnerabilities).
- **medium** — Issues that degrade quality, maintainability, or performance without an immediate user-visible defect (e.g., missing error boundaries, unstable references causing unnecessary re-renders, deprecated API usage).
- **low** — Minor deviations from best practices that are technically correct but could be improved (e.g., missing memo on a component that re-renders often but is not yet a bottleneck).

### Evidence Standard

Every finding must include **all** of the following. Findings missing any element must be dropped:

1. **Location** — Exact file path(s) and line number(s).
2. **Code snippet** — The specific code exhibiting the issue.
3. **What is wrong** — A clear, concrete explanation of the problem. Not "this could be better" but "this does X when it should do Y" or "this violates [specific standard/guideline]."
4. **Why it matters** — Concrete impact: who is affected, what breaks, what degrades, or what standard is violated. Reference the specific standard, guideline, or documentation (e.g., WCAG 2.1 SC 4.1.2, React docs on exhaustive-deps, framework migration guide).
5. **Suggested fix** — A concrete code change or approach, not a vague recommendation. Show the corrected code when possible.

### Verification Pass (Required)

After gathering findings from sub-agents, verify each one yourself:

1. Read the file at the cited path and confirm the line numbers are accurate.
2. Confirm the code snippet matches what is actually in the file.
3. Confirm the issue is real — not a false positive from misunderstanding the code's intent.
4. Confirm the suggested fix would not break existing behavior.
5. Drop any finding where verification fails.

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- No findings survive the verification pass.
- All findings are below the severity threshold.
- All findings are already tracked by open issues.
- All findings are subjective style preferences rather than concrete quality issues.
- You cannot provide specific file paths and line numbers for any finding.

### Consolidation Rules

- Group related findings (e.g., the same anti-pattern in multiple files) into a single numbered section.
- Prefer fewer, denser issues over frequent thin issues.
- If a pattern appears in many files, do a completeness pass: search the repo for all occurrences and list them, so maintainers can fix the whole family at once.

### Issue Format

**Issue title:** Brief summary of findings (e.g., "3 accessibility barriers in form components")

**Issue body:**

> ## Code Quality Audit — [Audit Dimension]
>
> The following issues were found during a scheduled audit. Each finding includes specific file locations, code evidence, and a suggested fix.
>
> **Severity threshold:** `${{ inputs.severity-threshold }}`
>
> ### 1. [Brief description]
>
> **Severity:** [high / medium / low]
> **File(s):** `path/to/file.ts` (lines N–M)
> **Standard/Guideline:** [What rule, best practice, or standard this violates — with a link if possible]
>
> **Current code:**
> ```
> [The problematic code snippet]
> ```
>
> **Problem:** [What is wrong and why it matters]
>
> **Suggested fix:**
> ```
> [The corrected code]
> ```
>
> ### 2. [Next finding...]
>
> ## Suggested Actions
>
> - [ ] [Specific, actionable checkbox for each fix]
