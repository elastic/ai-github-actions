# Contributing to AI GitHub Actions

Thank you for your interest in contributing! We welcome contributions from the community.

⚠️ IMPORTANT: This project requires agentic development using GitHub Copilot Agent. No local development environment is needed or expected.

🚫 Traditional Pull Requests Are Not Enabled: You cannot create pull requests directly. Instead, you create detailed agentic plans in issues, and GitHub Copilot Agent will create and implement the PR for you after maintainer approval.


## Why Agentic Development?

This project practices what it preaches: agentic workflows are used to build agentic workflows.

- **Dogfooding**: We use our own tools to build our tools
- **Consistency**: All changes go through the same automated quality gates
- **Accessibility**: No need to set up a local development environment
- **Focus on outcomes**: Describe what you want, not how to build it

## How to Contribute

### 1. Analyze with an Agent

Before filing an issue, use an agent to research the problem or feature. For bugs, have the agent identify root causes and propose fixes. For features, have it analyze the codebase and suggest an implementation approach.

**Issues submitted without agent analysis are likely to be deprioritized.**

### 2. Open an Issue with Your Agentic Plan

Create an issue with a complete, step-by-step implementation plan. The more detailed your plan, the better the agent can execute it.

**Example:**

```markdown
## Add timeout configuration to the mention-in-pr workflow

### Analysis
The current mention-in-pr workflow lacks a configurable timeout for the
agent step, which can cause workflows to hang when the model is
unresponsive.

### Implementation Plan

1. **Update the workflow source** (`.github/workflows/gh-aw-mention-in-pr.md`):
   - Add a `timeout` frontmatter field with default of 30 minutes
   - Wire it into the compiled lock file's job timeout

2. **Update the trigger example** (`gh-agent-workflows/mention-in-pr/example.yml`):
   - Add a comment showing how to override the timeout

3. **Update documentation** (`gh-agent-workflows/mention-in-pr/README.md`):
   - Document the new timeout input with example usage

4. **Recompile and validate**:
   - Run `make compile` to regenerate lock files
   - Run `make lint` to validate all workflows
```

### 3. Maintainer Assigns an Agent

Once approved, a maintainer assigns the issue to an AI agent. The agent creates a PR, implements your plan, runs validation, and responds to review feedback until the PR is merged.

You don't need to install anything or set up a local environment — the agent handles all of that.

## Issue Guidelines

- **Bugs**: Include agent analysis, root cause, proposed fix, and implementation plan
- **Features**: Explain the use case, provide examples, and include step-by-step instructions
- **Workflow failures**: Debug with an agent first, then report with analysis and remediation plan
- **Be specific**: Name the files, inputs, outputs, and test cases the agent should touch

## Security

If you discover a security vulnerability, please use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) — **do not** open a public issue. See [SECURITY.md](SECURITY.md) for details.

## Further Reading

- [Documentation site](https://elastic.github.io/ai-github-actions/)
- [Development guide](DEVELOPING.md) (reference for agents)
- [Code style](CODE_STYLE.md)
- [Security considerations](SECURITY.md)
- [Release process](RELEASE.md)
