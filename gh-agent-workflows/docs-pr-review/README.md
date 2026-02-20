# Docs PR Review

Docs PR review from an Elastic technical writer perspective. Reviews documentation changes for style guide compliance, `applies_to` tag correctness, and consistency with published Elastic documentation.

## What it checks

- **Vale linter output**: If Vale runs as a CI check in the repo, incorporates its findings and suggests fixes.
- **Elastic style guide**: Voice and tone, grammar and spelling, formatting, word choice, accessibility, and inclusivity.
- **`applies_to` tags**: Validates page-level, section-level, and inline applicability metadata against the cumulative docs guidelines.
- **Docs consistency**: Uses the Elastic docs MCP server to check for contradictions and inconsistencies with published documentation.

## Quick install

```bash
mkdir -p .github/workflows && curl -sL \
  https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-pr-review/example.yml \
  -o .github/workflows/docs-pr-review.yml
```

See [example.yml](example.yml) for the full workflow file.

## Trigger

Invoke by commenting `/docs-review` on any pull request.

| Event | Types | Condition |
| --- | --- | --- |
| `issue_comment` | `created` | Comment starts with `/docs-review` on a PR |

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `additional-instructions` | Repo-specific instructions appended to the agent prompt. | No | `""` |
| `setup-commands` | Shell commands run before the agent starts. | No | `""` |
| `intensity` | Review intensity (`conservative`, `balanced`, `aggressive`). | No | `balanced` |
| `minimum_severity` | Minimum severity for inline comments (`critical`, `high`, `medium`, `low`, `nitpick`). | No | `low` |

## Safe outputs

- `create-pull-request-review-comment` — inline review comments with suggested text fixes.
- `submit-pull-request-review` — submit the review (approve, request changes, or comment).
