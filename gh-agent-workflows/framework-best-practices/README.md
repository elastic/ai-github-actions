# Framework Best Practices

Find places where library-native features could replace hand-rolled solutions.

## How it works

Reads the project's dependency manifest (`package.json`, `go.mod`, `pyproject.toml`, etc.) to discover the tech stack, then scans the codebase for patterns that reinvent or work around library features — custom utilities that duplicate what a library already provides, state management anti-patterns, UI framework underuse, deprecated API styles, and missing framework optimizations. Only files an issue when a concrete simplification is found; most runs end with `noop`.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/framework-best-practices/example.yml \
  -o .github/workflows/framework-best-practices.yml
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

- `create-issue` — file a framework best practices report (max 1)
