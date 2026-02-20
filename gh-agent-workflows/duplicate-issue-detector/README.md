# Duplicate Issue Detector

Check whether a newly opened issue is a duplicate of an existing open or previously closed issue, and notify the reporter.

## How it works

When a new issue is opened, searches both open and closed issues using multiple targeted queries derived from the issue title and body. Posts a notice on the issue only when a strong duplicate match is found.

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
| `allowed-bot-users` | Allowlisted bot actors (comma-separated usernames) | No | `github-actions[bot]` |

## Safe Outputs

- `add-comment` — post a duplicate notice on the issue when a matching issue is found
