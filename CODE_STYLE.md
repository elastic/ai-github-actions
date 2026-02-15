# Code Style

Patterns and conventions unique to this codebase.

## Shared Scripts

Shared scripts live in a parent `scripts/` directory. RO and RWX variants reference them via:

```yaml
Bash(${{ github.action_path }}/../scripts/script-name.sh:*)
```

Workflow-specific scripts go in `claude-workflows/<workflow>/scripts/`.

## Tool Concatenation

`extra-allowed-tools` is appended to `allowed-tools` without replacing defaults:

```yaml
claude_args: |
  ${{ format('--allowedTools {0}{1}', inputs.allowed-tools, inputs.extra-allowed-tools != '' && format(',{0}', inputs.extra-allowed-tools) || '') }}
```

## Environment Variables for Scripts

Scripts receive configuration via environment variables set in the composite action's `env:` block (e.g. `PR_REVIEW_REPO`, `PR_REVIEW_PR_NUMBER`). Each script documents its required variables in its header comment.

## Prompt Sections

Prompts use XML-like sections: `<context>`, `<task>`, `<constraints>`, `<allowed_tools>`, `<additional_instructions>`, plus workflow-specific sections.

## Standard Footer

All comments and reviews include this footer:

```
---
[Why is Claude responding?](https://ela.st/github-ai-tools) | Type `@claude` to interact further

Give us feedback! React with 🚀 if perfect, 👍 if helpful, 👎 if not.
```

## File Convention

Every workflow action has three files: `action.yml`, `example.yml`, `README.md`.
