# Migration Guide: Claude Workflows → GitHub Agent Workflows

This guide shows how to convert your Claude Composite Action workflows to GitHub Agent Workflows.

## Update the Secret

GitHub Agent Workflows use a different secret name:

- **Old:** `CLAUDE_CODE_OAUTH_TOKEN`
- **New:** `COPILOT_GITHUB_TOKEN`

Set `COPILOT_GITHUB_TOKEN` in your repository settings with the same value as your existing `CLAUDE_CODE_OAUTH_TOKEN`.

## Convert Workflow Syntax

### Key Changes

1. Use reusable workflows instead of composite actions
2. No manual `actions/checkout` step
3. Pass secrets via `secrets:` block
4. Pass configuration via `with:` block

### Examples

| Old (Claude) | New (GitHub Agent) |
| --- | --- |
| [mention-in-pr/rwx](https://github.com/elastic/ai-github-actions/blob/main/claude-workflows/mention-in-pr/rwx/example.yml) | [mention-in-pr](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/mention-in-pr/example.yml) |
| [mention-in-issue/rwx](https://github.com/elastic/ai-github-actions/blob/main/claude-workflows/mention-in-issue/rwx/example.yml) | [mention-in-issue](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/mention-in-issue/example.yml) |
| [pr-review/rwx](https://github.com/elastic/ai-github-actions/blob/main/claude-workflows/pr-review/rwx/example.yml) | [pr-review](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/pr-review/example.yml) |
| [issue-triage/rwx](https://github.com/elastic/ai-github-actions/blob/main/claude-workflows/issue-triage/rwx/example.yml) | [issue-triage](https://github.com/elastic/ai-github-actions/blob/main/gh-agent-workflows/issue-triage/example.yml) |

## Workflow Mapping

| Claude Workflow | GitHub Agent Workflow |
| --- | --- |
| `claude-workflows/mention-in-pr/rwx` | `gh-aw-mention-in-pr.lock.yml` |
| `claude-workflows/mention-in-pr/rwxp` | `gh-aw-mention-in-pr.lock.yml` |
| `claude-workflows/mention-in-issue/rwx` | `gh-aw-mention-in-issue.lock.yml` |
| `claude-workflows/mention-in-issue/rwxp` | `gh-aw-mention-in-issue.lock.yml` |
| `claude-workflows/pr-review/ro` | `gh-aw-pr-review.lock.yml` |
| `claude-workflows/pr-review/rwx` | `gh-aw-pr-review.lock.yml` |
| `claude-workflows/issue-triage/ro` | `gh-aw-issue-triage.lock.yml` |
| `claude-workflows/issue-triage/rwx` | `gh-aw-issue-triage.lock.yml` |

## Checklist

- [ ] Add `COPILOT_GITHUB_TOKEN` secret
- [ ] Update workflow files (see examples above)
- [ ] Remove `actions/checkout` steps
- [ ] Test workflows
