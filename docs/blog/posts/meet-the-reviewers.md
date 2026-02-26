---
date: 2026-02-05
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Reviewers

You open a PR. Before you can ping a teammate, the review is already in progress. By the time you switch back to the tab, there are inline comments on three files — severity-ranked, with explanations. A minute later, a commit lands on your branch fixing two of them. You didn't ask anyone. The Reviewers showed up on their own.

<!-- more -->

This is the Reviewers squad: five agents that handle the entire pull request lifecycle, from first review to final description. They're the most visible agents in the factory because they show up on every PR, every day, in every repo that runs them. Here's who they are and what they actually do.

## [PR Review](../../workflows/gh-agent-workflows/pr-review.md) — The First Responder

PR Review is the workhorse. It triggers on `pull_request` events — opened, updated, reopened, ready for review — and posts a file-by-file code review with severity-ranked inline comments. It runs on Copilot with gpt-5.3-codex, and it reviews at configurable intensity. The default is aggressive, which means it will flag real issues, not just style nits.

What makes PR Review interesting is what happens after the review. If it finds genuine problems — logic errors, missing edge cases, security concerns — it can dispatch Mention in PR to go fix them. The agent reviews your code, decides something is wrong, and then calls in another agent to push a fix. All of this happens through guarded safe-output tools: the only things PR Review can do are post review comments and submit a review. It cannot merge, cannot push code, cannot modify labels. Narrow scope, real impact.

There's also a [PR Review (Fork)](../../workflows/gh-agent-workflows/pr-review-fork.md) variant built on `pull_request_target` for reviewing PRs from forks. Same review logic, different trigger model, because GitHub's security model requires it.

## [PR Review Addresser](../../workflows/gh-agent-workflows/pr-review-addresser.md) — The Follow-Through

Finding problems is only half the job. PR Review Addresser is the agent that actually fixes what PR Review flags. After PR Review posts its comments, PR Review Addresser picks them up, analyzes the feedback, writes the fix, and pushes a commit to the branch.

It also runs on Copilot with gpt-5.3-codex, and it's designed to work in tight coordination with PR Review. Think of it as the second half of a two-step loop: review, then address. The result is that many review comments get resolved before a human even reads them. You come back to a PR that's already cleaner than when you left it.

## [Mention in PR](../../workflows/gh-agent-workflows/mention-in-pr.md) — The Fixer

Mention in PR is the human-coordinated agent. Drop `/ai` in a PR comment — followed by what you want — and this agent reviews the relevant code, writes a fix, and pushes it to the branch. It's the agent you invoke when you know exactly what needs to happen but don't want to context-switch into the code yourself.

It runs on Copilot with gpt-5.3-codex and responds to `issue_comment` triggers on PRs. We use it constantly. "Fix the typo on line 42." "Add input validation to this function." "Refactor this block to use the new helper." It handles all of these.

There are two variants worth knowing about. The "no sandbox" variant runs without the default sandboxed execution environment, for cases where the fix requires tooling that isn't available in the sandbox. And Trigger Mention in PR by ID is a workflow-dispatch variant that lets other agents or automation invoke it programmatically by PR number — which is exactly how PR Review dispatches it when it finds issues worth fixing.

## [Update PR Body](../../workflows/gh-agent-workflows/update-pr-body.md) — The Scribe

Every PR needs a good description, and nobody wants to write one. Update PR Body reads the diff and any linked issues, then auto-populates the PR description with a clear summary of what changed and why. It triggers on `pull_request` events — opened, updated, ready for review — so the description stays accurate as the branch evolves.

This sounds simple, and it is. But it solves a real problem. PRs that sit in review with a blank description, or a description that was accurate three days and twelve commits ago, slow everyone down. Update PR Body keeps the description clean and current throughout the PR lifecycle, so reviewers always know what they're looking at.

## [Estc Docs PR Review](../../workflows/gh-agent-workflows/estc-docs-pr-review.md) — The Style Guide Enforcer

Docs PR Review is the specialist. Invoke it with the `/docs-review` command on a PR, and it reviews documentation changes for style guide compliance, `applies_to` frontmatter correctness, and overall consistency. It's human-coordinated — you call it when you want a docs-specific review on top of the standard code review.

This agent exists because documentation has different quality criteria than code. A code reviewer catches logic bugs. Docs PR Review catches tone inconsistencies, missing frontmatter fields, and style guide violations that would otherwise slip through to production. Different lens, same PR.

## How They Work Together

The Reviewers aren't five independent agents that happen to run on PRs. They're a pipeline. PR Review fires first, posting its file-by-file analysis. PR Review Addresser picks up the findings and pushes fixes. Meanwhile, Update PR Body keeps the description in sync with every change — including the ones the agents just made. When a developer needs something specific, they drop `/ai` in a comment and Mention in PR handles it on demand. And if the PR touches docs, `/docs-review` brings in the style guide enforcer for a specialized pass. Together, they cover the full PR lifecycle: review, fix, describe, and refine. By the time a human reviewer sits down to look at the PR, a significant amount of the mechanical work is already done.

## Try It

Pick a workflow, copy the `example.yml` into your repo's `.github/workflows/` directory, and you're running. The [workflow docs](../../workflows/gh-agent-workflows.md) have the full setup instructions, example configurations, and details on every parameter.

If you're just getting started with the factory, read [Welcome to the Agent Factory](welcome-to-the-factory.md) first for the big picture — then come back here and turn on PR Review. It's the one agent we'd recommend to every team.
