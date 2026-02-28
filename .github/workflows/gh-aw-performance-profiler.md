---
inlined-imports: true
name: "Performance Profiler"
description: "Identify hot paths, profile code, and propose meaningful performance improvements"
imports:
  - gh-aw-fragments/elastic-tools.md
  - gh-aw-fragments/runtime-setup.md
  - gh-aw-fragments/ensure-full-history.md
  - gh-aw-fragments/formatting.md
  - gh-aw-fragments/rigor.md
  - gh-aw-fragments/mcp-pagination.md
  - gh-aw-fragments/messages-footer.md
  - gh-aw-fragments/safe-output-create-issue.md
  - gh-aw-fragments/previous-findings.md
  - gh-aw-fragments/pick-three-keep-one.md
  - gh-aw-fragments/scheduled-audit.md
  - gh-aw-fragments/network-ecosystems.md
engine:
  id: copilot
  model: ${{ inputs.model }}
on:
  workflow_call:
    inputs:
      model:
        description: "AI model to use"
        type: string
        required: false
        default: "gpt-5.3-codex"
      additional-instructions:
        description: "Repo-specific instructions appended to the agent prompt"
        type: string
        required: false
        default: ""
      setup-commands:
        description: "Shell commands to run before the agent starts (dependency install, build, etc.)"
        type: string
        required: false
        default: ""
      allowed-bot-users:
        description: "Allowlisted bot actor usernames (comma-separated)"
        type: string
        required: false
        default: "github-actions[bot]"
      messages-footer:
        description: "Footer appended to all agent comments and reviews"
        type: string
        required: false
        default: ""
      title-prefix:
        description: "Title prefix for created issues (e.g. '[performance-profiler]')"
        type: string
        required: false
        default: "[performance-profiler]"
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
  roles: [admin, maintainer, write]
  bots:
    - "${{ inputs.allowed-bot-users }}"
concurrency:
  group: performance-profiler
  cancel-in-progress: true
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    toolsets: [repos, issues, pull_requests, search, labels]
  bash: true
  web-fetch:
strict: false
safe-outputs:
  activation-comments: false
  noop:
  create-issue:
    max: 1
    title-prefix: "${{ inputs.title-prefix }} "
    close-older-issues: false
    expires: 7d
timeout-minutes: 90
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
---

Identify performance hot paths in the repository, profile the code, and report findings with concrete before/after evidence.

**The bar is high: you must produce measurable profiling data before filing.** Most runs should end with `noop` — that means no meaningful optimization opportunity was found.

### Data Gathering

1. Detect the primary language and build system:
   - Check for `go.mod`, `package.json`, `pyproject.toml`, `Gemfile`, `Cargo.toml`, `pom.xml`, `build.gradle`, or similar.
   - Identify test and benchmark commands from README, CONTRIBUTING, DEVELOPING, Makefile, CI config, or similar.
2. Look for existing benchmarks:
   - **Go**: `grep -r "func Benchmark" --include="*_test.go"` for Go benchmark functions.
   - **Node.js/JS**: Search for benchmark scripts in `package.json`, or files matching `bench*`, `perf*`.
   - **Python**: Search for `pytest-benchmark`, `timeit`, or benchmark scripts.
   - **Rust**: Search for `#[bench]` or criterion benchmarks.
   - **Java**: Search for JMH benchmarks or `@Benchmark` annotations.
3. If existing benchmarks are found, run them and capture baseline results.
4. Use the **Pick Three, Keep One** pattern for the data gathering phase: spawn 3 `general-purpose` sub-agents (with `model: "${{ inputs.model }}"`), each searching for performance opportunities from a different angle (e.g., different performance dimensions such as CPU-bound vs. memory-allocation vs. I/O-bound paths, different code paths or entry points, different bottleneck types such as algorithmic complexity vs. redundant work vs. expensive serialization). Include the language/build system info, existing benchmark results, and the full "What to Report" / "What to Skip" criteria in each sub-agent prompt. Each sub-agent should return its best candidate hot path with evidence or recommend `noop`.
5. If no existing benchmarks exist, identify likely hot paths:
   - Find functions called frequently from main entry points (CLI commands, API handlers, request paths).
   - Look for loops over large data structures, repeated I/O, expensive string operations, or known anti-patterns.
   - Use `git log --since="28 days ago" --stat` to find recently changed performance-sensitive areas.
### Profiling

Generate concrete profiling data — do not speculate about performance based on code reading alone.

- **Go**: Run benchmarks with `go test -bench=. -benchmem -cpuprofile=cpu.prof -memprofile=mem.prof -count=5`. Use `go tool pprof` to identify top functions. If no benchmarks exist, write a minimal benchmark for the identified hot path.
- **Node.js**: Use `--prof` flag or `perf_hooks` to measure execution time. Run benchmarks with multiple iterations.
- **Python**: Use `cProfile`, `timeit`, or `pytest-benchmark`. Capture function-level timing.
- **Rust**: Use `cargo bench` with criterion or the built-in bench harness. Capture timing and throughput.
- **Java**: Use JMH benchmarks. Capture throughput and average time.
- For other languages, use the idiomatic profiling tool for that ecosystem.

Always capture **baseline numbers** before making any change.

### Optimization

1. Based on profiling data, identify the single most impactful optimization opportunity.
2. Implement the smallest safe change that improves the hot path. Examples:
   - Replace O(n²) algorithm with O(n log n) or O(n).
   - Reduce unnecessary allocations (pre-allocate slices, reuse buffers).
   - Cache repeated computations.
   - Avoid redundant I/O or network calls.
   - Replace expensive regex with string operations where possible.
   - Use more efficient data structures (maps vs linear search).
3. Re-run the same profiling or benchmark to capture **after** numbers.
4. Verify existing tests still pass — run the most relevant test command(s).

### What to Report

Only file an issue if **all** of these are true:
- You have concrete before/after benchmark or profiling numbers.
- The improvement is **not trivial** (at least 10% improvement in time or memory for the hot path, or measurably significant for high-frequency operations).
- Existing tests pass after the change.
- The change is behavior-preserving — no functional regressions.

### What to Skip

- Micro-optimizations with <10% improvement — not worth a human's time to review.
- Theoretical performance concerns without profiling data — **no "this looks slow."**
- Optimizations that sacrifice readability for marginal gains.
- Changes that alter public APIs or behavior.
- Performance issues already tracked by an open issue.

### Quality Gate — When to Noop

Call `noop` if any of these are true:
- No existing benchmarks were found and you could not write a meaningful one.
- Profiling did not reveal a clear hot path.
- The best optimization you found yields less than 10% improvement.
- You could not verify that existing tests still pass after the change.
- A similar issue is already open.
- The repository has no performance-sensitive code paths worth optimizing.

### Issue Format

**Issue title:** Short description of the optimization opportunity

**Issue body:**

> ## Hot Path
> [Which function/code path is the bottleneck, with file path and line numbers]
>
> ## Profiling Data
> **Before:**
> ```
> [Baseline benchmark or profiling output]
> ```
>
> ## Proposed Change
> [Description of the optimization, with a diff or code snippet]
>
> ## Results
> **After:**
> ```
> [Post-optimization benchmark or profiling output]
> ```
>
> **Improvement:** [Percentage improvement in time/memory/throughput]
>
> ## Verification
> - [Tests run and their results]
> - [Confirmation that behavior is preserved]
>
> ## Evidence
> - [Commands run, full profiling output, file references]

### Labeling

- If a `performance` label exists (check with `github-get_label`), include it in the `create_issue` call. Otherwise, if `performance-profiler` exists, use that. If neither exists, rely on the `${{ inputs.title-prefix }}` title prefix only.

${{ inputs.additional-instructions }}
