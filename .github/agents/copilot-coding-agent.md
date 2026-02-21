---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name: default-agent
description: The default agent
---

## Repository Context

@AGENTS.md

## Development

@DEVELOPING.md

## Code Style

@CODE_STYLE.md

## Prompt Fragments

Follow these guidelines from the shared prompt fragments:

@.github/workflows/gh-aw-fragments/formatting.md

@.github/workflows/gh-aw-fragments/rigor.md

@.github/workflows/gh-aw-fragments/workflow-edit-guardrails.md

## Instructions

Understand the request, investigate the codebase, and respond with a helpful, actionable answer.

### Step 1: Gather Context

1. Read the full issue thread to understand the discussion so far.
2. If the issue references other issues or PRs, read each to understand the broader context.
3. Use `grep` and file reading to explore the relevant parts of the codebase.

### Step 2: Investigate and Implement

Based on the request, do what's appropriate:

- **Answer questions** about the codebase — find the relevant code and explain it.
- **Debug reported problems** — reproduce locally, run required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config, and trace the code path.
- **Implement changes** — make the changes and verify they work by running `make compile` and `make lint`.
- **Clarify requirements** — ask follow-up questions if the request is ambiguous.

### Step 3: Verify Changes

When making code changes, identify and run required repo commands (lint/build/test) from README, CONTRIBUTING, DEVELOPING, Makefile, or CI config and include results. If required commands cannot be run, explain why.

For this repository:

```bash
make compile          # sync triggers + compile to lock files
make lint             # run all linters
```

### Step 4: Final Review

Before finishing, take a step back and critically review your work:

1. **Re-read the original issue** — confirm every requirement and acceptance criterion is addressed. If the issue has multiple parts, verify each one individually.
2. **Double-check your changes** — review each modified file. Look for typos, missed edge cases, inconsistencies, and unintended side effects.
3. **Verify completeness** — ask yourself: "If I were the issue author, would I consider this done?" If not, identify what's missing and address it.
4. **Run verification commands one final time** — ensure `make compile` and `make lint` still pass after all changes.
