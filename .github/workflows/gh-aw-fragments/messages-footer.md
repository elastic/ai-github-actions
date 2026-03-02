---
safe-outputs:
  messages:
    footer: "${{ inputs.messages-footer || format('---\n[What is this?](https://ela.st/github-ai-tools) | [From workflow: {0}]({{run_url}})\n\nGive us feedback! React with 🚀 if perfect, 👍 if helpful, 👎 if not.', github.workflow) }}"
---

## Message Footer

A footer is automatically appended to all comments and reviews. Do not add your own footer or sign-off — the runtime handles this.
