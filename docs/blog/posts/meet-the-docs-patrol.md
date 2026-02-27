---
date: 2026-02-18
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Docs Patrol

Code changes. Docs don't. These agents make sure they stay in sync.

<!-- more -->

Documentation rot is one of the most predictable problems in software engineering. A function gets renamed, a configuration flag gets deprecated, an onboarding step changes — and the docs that reference them quietly become wrong. Nobody notices until a new contributor follows the guide and hits a wall. We built the Docs Patrol agents to close that gap automatically.

## [Docs Patrol](../../workflows/gh-agent-workflows/docs-patrol.md)

This agent runs on a weekday schedule and scans for stale internal documentation — READMEs, inline docs, and any other documentation that lives inside the repository. It operates as a detector: it identifies places where the docs have drifted from the code. There is no dedicated fixer paired with it yet, so when it finds staleness it opens an issue describing what is out of date and what changed. A human still makes the call on how to update the wording, but the hard part — noticing the drift in the first place — is handled.

## [Docs Patrol External (Elastic-specific)](../../workflows/gh-agent-workflows/estc-docs-patrol-external.md)

Same concept, different scope. This agent also runs on a weekday schedule, but instead of scanning internal docs it scans published Elastic documentation for references that have fallen out of date with the codebase. Published docs are even more dangerous when they go stale because they reach a wider audience and carry more authority. If the public docs say a parameter is required but the code made it optional three releases ago, that is a real problem. This agent catches it.

## [Docs PR Review (Elastic-specific)](../../workflows/gh-agent-workflows/estc-docs-pr-review.md)

This one is not scheduled — it is triggered by the `/docs-review` command on pull requests. When someone opens a PR that touches documentation, they can invoke this agent to review the changes for style guide compliance, correct `applies_to` frontmatter, and consistency with existing docs. It is human-coordinated: you decide when to call it and on which PRs. Think of it as a specialized reviewer that never forgets the style guide.

## [Newbie Contributor Patrol](../../workflows/gh-agent-workflows/newbie-contributor-patrol.md) and [Newbie Contributor Fixer](../../workflows/gh-agent-workflows/newbie-contributor-fixer.md)

These run on a weekday schedule as a detector/fixer pair. The Newbie Contributor Patrol scans for onboarding documentation gaps — things a new contributor would struggle with. Missing setup steps, unexplained prerequisites, jargon without context. When it finds gaps, the Newbie Contributor Fixer creates PRs to fill them. There is also an External variant that cross-references published documentation to make sure the public onboarding path is just as clear as the internal one.

## How They Complement Each Other

These agents cover documentation from four angles. Docs Patrol catches internal staleness — the READMEs and inline docs that drift as code evolves. Docs Patrol External catches published doc drift — the user-facing documentation that carries the most weight and the most risk when it goes wrong. Docs PR Review enforces quality on new documentation as it is written, before it merges. And the Newbie Contributor Patrol ensures the onboarding path is clear, filling the gaps that existing contributors have long since stopped noticing.

Together, they form a feedback loop: existing docs stay accurate, new docs meet the bar, published docs stay current, and the onboarding experience stays navigable.

## Try It

These agents are all built on the workflow library we ship as part of the AI Software Factory. You can configure and deploy them in your own repositories using the [GitHub Agent Workflows](../../workflows/gh-agent-workflows.md) documentation.

For the full picture of how the factory works, head back to [Welcome to the Factory](welcome-to-the-factory.md).
