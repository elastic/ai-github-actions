# Create Comment On Issue

Add an AI-generated comment to a specific issue by number. Use this when you need to comment on an issue from a `workflow_call` (e.g., chaining from a detector) rather than from an issue comment trigger.

**Mention in Issue** targets the issue that triggered the workflow (e.g., via an `/ai` comment). **Create Comment On Issue** takes `target-issue-number` as an input, so you can chain it from any workflow that produces an issue number.

## Quick install

Chain from a detector that creates issues:

```yaml
jobs:
  detect:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-bug-hunter.lock.yml@v0
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}

  comment:
    needs: detect
    if: needs.detect.outputs.created_issue_number != ''
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-create-comment-on-issue.lock.yml@v0
    with:
      target-issue-number: ${{ needs.detect.outputs.created_issue_number }}
      prompt: "Summarize the bug and suggest next steps for the reporter."
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

Or call it directly with any issue number (e.g., from `workflow_dispatch`):

```yaml
jobs:
  comment:
    uses: elastic/ai-github-actions/.github/workflows/gh-aw-create-comment-on-issue.lock.yml@v0
    with:
      target-issue-number: "123"
      prompt: "Analyze this issue and provide implementation guidance."
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

## Trigger

| Event | Description |
| --- | --- |
| `workflow_call` | Invoked by another workflow with `target-issue-number` |

## Inputs

| Input | Description | Default |
| --- | --- | --- |
| `target-issue-number` | Issue number to comment on | *(required)* |
| `prompt` | Instructions for what to include in the comment | `""` |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt | `""` |
| `setup-commands` | Shell commands run before the agent starts | `""` |
| `model` | AI model to use | `gpt-5.3-codex` |
| `messages-footer` | Footer appended to the comment | `""` |

## Safe outputs

- `add-comment` — add a comment to the targeted issue (max 1)

## When to use

| Workflow | Use when |
| --- | --- |
| [Mention in Issue](mention-in-issue.md) | User reacts with `/ai` on an issue — targets the triggering issue |
| **Create Comment On Issue** | You have an issue number from a prior job (e.g., detector output) and want to add a comment |
