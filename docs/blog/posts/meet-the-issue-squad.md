---
date: 2026-02-10
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Issue Squad

A new issue lands. Within seconds, it's labeled, prioritized, and checked against every existing issue for duplicates. No human triaged it. No one assigned a label from a dropdown. The Issue Squad handled it — seven agents that collectively own the entire lifecycle of a GitHub issue, from the moment it's filed to the moment it's closed.

<!-- more -->

This is the squad we reach for when someone asks "what does agentic issue management actually look like?" It's not one agent doing everything. It's a pipeline of specialists, each with a narrow job and a clear trigger, working together so that issues never sit unread.

## The Roster

**[Issue Triage](../../workflows/gh-agent-workflows/issue-triage.md) — The First Responder.** This is the agent that fires the instant a new issue is created. It reads the issue, investigates the codebase for relevant context, and posts a structured analysis: what the issue is about, which files are likely involved, how severe it looks, and a recommended set of next steps. It runs on Copilot with gpt-5.3-codex, and it's fast — most investigations land within a minute of the issue being filed. Think of it as the ER doctor who does the initial assessment before deciding which specialist to page.

**[Duplicate Issue Detector](../../workflows/gh-agent-workflows/duplicate-issue-detector.md) — The Memory.** This one also triggers on every new issue, running in parallel with Triage. Its job is singular: check the new issue against every open issue and every recently closed issue, looking for duplicates or near-duplicates. When it finds a match, it posts a comment linking to the existing issue with an explanation of why it thinks they're related. This saves a surprising amount of time. In active repositories, duplicate issues are more common than you'd expect, and catching them early prevents fragmented discussions and wasted investigation.

**[Issue Fixer](../../workflows/gh-agent-workflows/issue-fixer.md) — The Go-Getter.** Issue Fixer is what happens when you take Issue Triage and remove the guardrails. It triggers on new issues just like Triage, but instead of stopping at an investigation and a plan, it goes further — for straightforward fixes, it opens a draft PR with the proposed change. Not every issue gets a PR (it's not reckless), but for clear-cut bugs with obvious fixes, having a draft PR waiting by the time a developer reads the issue is genuinely useful. It runs on Copilot with gpt-5.3-codex and is best suited for repositories where many issues are small, concrete, and well-described.

**[Mention in Issue](../../workflows/gh-agent-workflows/mention-in-issue.md) — The On-Call Expert.** This is the human-coordinated agent. Type `/ai` in any issue comment followed by a question, and this agent wakes up to help. It can answer questions about the codebase, debug problems, investigate edge cases, and even create PRs when asked. It's the agent you invoke when the automated pipeline has done its job but you need to go deeper. There's also a "no sandbox" variant for cases where the agent needs broader system access to investigate properly.

**[Stale Issues](../../workflows/gh-agent-workflows/stale-issues.md) — The Closer.** Every weekday, this agent reviews open issues and checks whether any of them have been silently resolved. Maybe a recent PR fixed the underlying bug. Maybe the feature was shipped under a different ticket. Maybe the issue just isn't relevant anymore. Stale Issues finds these cases and flags them for closure. It's a janitor, and janitors are underrated. Open issue counts that only go up are demoralizing; this agent keeps the backlog honest.

**[Plan](../../workflows/gh-agent-workflows/plan.md) — The Architect.** Triggered by the `/plan` command in an issue comment, this agent generates a structured implementation plan. It breaks down the work into logical steps, identifies affected files, considers edge cases, and can optionally create sub-issues for each piece of the plan. It's the agent you call when an issue is clearly important but nobody has sat down to figure out what "done" actually looks like.

**[Deep Research](../../workflows/gh-agent-workflows/internal-gemini-cli-web-search.md) — The Scholar.** Triggered by `/research` in an issue comment, and here's the interesting part: this is the one agent in the entire factory that doesn't use GitHub Copilot. Deep Research runs on Google Gemini (gemini-3-pro-preview) with extended investigation capabilities. We chose Gemini here because research tasks benefit from its deeper context handling and broader reasoning window. It requires a separate GEMINI_API_KEY, and it's purpose-built for questions that need more than a quick codebase scan — think architectural decisions, technology comparisons, or debugging problems that span multiple systems.

## The Pipeline

These agents aren't isolated. They form a natural pipeline that handles the full lifecycle of an issue:

A new issue arrives. **Triage** labels it and posts an investigation. In parallel, **Duplicate Detector** checks whether it's been filed before. If the issue is a straightforward fix, **Issue Fixer** opens a draft PR. If the issue needs a more detailed breakdown, a developer invokes **Plan** to generate an implementation strategy. If the issue requires deep investigation — maybe it involves an unfamiliar dependency or an architectural question — **Deep Research** takes over with Gemini's extended reasoning. Throughout all of this, **Mention in Issue** is available on demand for any question or task a human wants to delegate. And in the background, **Stale Issues** sweeps through the backlog every weekday, closing what's been resolved.

The result is that issues move from "filed" to "understood" to "in progress" with minimal human overhead. Developers still make the decisions — which PRs to merge, which plans to approve, which issues to prioritize — but the busywork of initial triage, duplicate checking, and backlog grooming is handled automatically.

## Try It

The Issue Squad workflows are available in the [gh-agent-workflows](../../workflows/gh-agent-workflows.md) directory. Each one comes with an example workflow file you can drop into your repository. Start with Issue Triage and Duplicate Detector — they're the lowest-risk, highest-value pair.

If you're new to the factory, start with the [welcome post](welcome-to-the-factory.md) for the full picture of all 40+ agents and how they fit together.
