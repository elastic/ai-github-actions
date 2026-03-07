Analyze the codebase for quality issues and file a structured report when concrete, actionable findings exist.

**The bar is high: only report issues backed by specific code evidence.** Most runs should end with `noop` — that means the code is in good shape for the dimension being audited. Filing nothing is a success when there is nothing worth filing.

### Severity Threshold: `${{ inputs.severity-threshold }}`

Only include findings at or above the configured severity. Severity labels and meanings are defined by the importing workflow; this fragment uses the importing workflow's `${{ inputs.severity-threshold }}` semantics.

### Evidence Standard

Every finding must include **all** of the following. Findings missing any element must be dropped:

1. **Location** — File path(s) and precise location context (line numbers when available or another unambiguous locator required by the importing workflow).
2. **Evidence** — The specific code or configuration that exhibits the issue.
3. **What is wrong** — A clear, concrete explanation of the problem. Not "this could be better" but "this does X when it should do Y" or "this violates [specific standard/guideline]."
4. **Why it matters** — Concrete impact: who is affected, what breaks, what degrades, or what standard is violated. Reference the specific standard, guideline, or documentation (e.g., WCAG 2.1 SC 4.1.2, React docs on exhaustive-deps, framework migration guide).
5. **Suggested fix** — A concrete code change or approach, not a vague recommendation.

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

### Output Contract

Follow the importing workflow's issue title/body template. This shared fragment defines quality gates and evidence requirements only; per-workflow report schemas remain source-of-truth for final output format.
