# Small Problem Fixer

Find small, related issues and open a focused PR.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/small-problem-fixer/example.yml \
  -o .github/workflows/small-problem-fixer.yml
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

- `create-pull-request` — open a PR with the fix
