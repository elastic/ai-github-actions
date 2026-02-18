# Code Simplifier

Simplify overcomplicated code with high-confidence refactors.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-simplifier/example.yml \
  -o .github/workflows/code-simplifier.yml
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

## Safe Outputs

- `create-pull-request` — open a PR with simplification changes
