# Duplicate Issue Detector

Check whether a newly opened issue is a duplicate of an existing open or previously closed issue, and notify the reporter.

## Quick Install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/duplicate-issue-detector/example.yml \
  -o .github/workflows/duplicate-issue-detector.yml
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

## Safe Outputs

- `add-comment` — post a duplicate notice on the issue when a matching issue is found
