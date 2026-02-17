---
imports:
  - gh-aw-workflows/scheduled-report-rwx.md
---

Find a single reproducible, user-impacting bug in the repository that can be covered by a minimal failing test.

### Data Gathering

1. Review recent changes:
   - Run `git log --since="14 days ago" --stat` and identify candidates with user-facing impact.
   - Read the diffs and related files for each candidate.
2. Check for existing reports:
   - Search open issues for similar symptoms or areas before filing a new issue.
3. Reproduce locally:
   - Use the smallest relevant command from the docs or Makefile to trigger the behavior (for example `make compile` or `scripts/dogfood.sh`).
   - Capture the exact steps and output.

### What to Look For

- Clear user impact: command failure, incorrect output, broken workflow, or misconfiguration.
- Deterministic reproduction (not flaky).
- Can be expressed as a minimal failing test (unit, CLI, or workflow compilation step).

### What to Skip

- Theoretical concerns without a reproduction.
- Issues that require large refactors or design changes.
- Behavior already tracked by an open issue.

### Issue Format

**Issue title:** Short bug summary

**Issue body:**

> ## Impact
> [Who/what is affected, why it matters]
>
> ## Reproduction Steps
> 1. ...
>
> ## Expected vs Actual
> **Expected:** ...
> **Actual:** ...
>
> ## Suggested Failing Test
> [File path + outline of test]
>
> ## Evidence
> - [Commands/output, file references, or links]
