# Performance Profiler

Identify hot paths, profile code, and propose meaningful performance improvements.

## How it works

Detects the build system and benchmark infrastructure, runs existing benchmarks or instruments likely hot paths, and reports findings with concrete before/after measurements. The bar is high — files only when measurable profiling data supports the claim. Most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/performance-profiler/example.yml \
  -o .github/workflows/performance-profiler.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Schedule |
| --- | --- |
| `schedule` | Weekdays |
| `workflow_dispatch` | Manual |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |

## Safe Outputs

- `create-issue` — file a performance profiling report (max 1, auto-closes older reports)
