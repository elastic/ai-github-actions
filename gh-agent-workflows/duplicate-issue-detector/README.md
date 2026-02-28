# Duplicate Issue Detector

Check whether a newly opened issue is a duplicate of, or highly related to, an existing open or previously closed issue, and notify the reporter.

## How it works

When a new issue is opened, a prescan step fetches the newest 500 and oldest 500 issues (number, title, state) into a local index file, then de-duplicates any overlap between those ranges. The agent then scans this index for obvious title matches before running targeted search queries against both open and closed issues. Posts a notice on the issue when a strong duplicate match is found, or a lighter "highly related" notice when issues are closely related but distinct.

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
| `allowed-bot-users` | Allowlisted bot actor usernames (comma-separated) | No | `github-actions[bot]` |
| `detect-related-issues` | Set to `"false"` to skip detection of highly related (but not duplicate) issues | No | `"true"` |

## Safe Outputs

- `add-comment` — post a duplicate or highly-related notice on the issue when a matching issue is found
