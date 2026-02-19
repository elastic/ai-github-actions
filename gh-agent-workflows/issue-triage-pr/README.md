# Issue Triage (Optional PRs)

Investigate new issues and provide triage analysis, with optional automatic PR creation controlled by workflow inputs.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-triage-pr/example.yml \
  -o .github/workflows/issue-triage-pr.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

| Event | Types |
| --- | --- |
| `issues` | `opened` |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | No | `""` |
| `setup-commands` | Shell commands run before the agent starts | No | `""` |
| `automatic-prs` | Allow automatic PR creation for straightforward fixes | No | `"false"` |
| `draft-prs` | Create PRs as draft when PR creation is enabled | No | `"true"` |

## Safe Outputs

- `add-comment` — post triage analysis on the issue
- `create-pull-request` — open a PR when `automatic-prs` is enabled and a verified fix is implemented
