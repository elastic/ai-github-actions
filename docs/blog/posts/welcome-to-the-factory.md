---
date: 2026-02-04
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Welcome to the Agent Factory

*40+ AI agents. Zero new tabs to monitor. Your repo runs itself.*

We built a fleet of specialized AI agents that review PRs, hunt bugs, triage issues, investigate CI failures, generate feature ideas, and audit your docs — all running as GitHub Actions on the [Elastic AI Software Factory](https://github.com/elastic/ai-github-actions) framework. This is our agent factory.

<!-- more -->

## What Is This?

The Elastic AI Software Factory is a collection of 40+ AI-powered GitHub Actions workflows. They run on schedules and event triggers — PRs opened, issues filed, CI failures detected. Most use GitHub Copilot with gpt-5.3-codex. They're real, running in production on real repositories, not demos.

These agents actually do things like:

- **Review every PR file-by-file** and post severity-ranked inline comments — then dispatch themselves to go fix what they find
- **Read CI failure logs** and diagnose the root cause before you've finished your coffee
- **Hunt for bugs daily** — and expect to find nothing (a healthy codebase is a success)
- **Generate domain-specific feature ideas** daily using custom audit agents, each from a different persona
- **Run Playwright smoke tests** silently every weekday morning using custom audit agents — you only hear from them when something breaks
- **Triage every new issue** within seconds — labeling, prioritizing, and checking for duplicates automatically
- **Audit your docs** for staleness, scanning both internal and published documentation

Every agent operates through GitHub's native interface. Issues, PR comments, review threads — the same surfaces your team already watches. No new dashboards. No vendor portal. Just your repo, working harder.

## Why Build a Factory?

Honest answer: we wanted to explore what happens when you go all-in on agentic workflows. Not a single "AI assistant" bolted onto a repo, but a full fleet of specialists, each with a clear mission and a narrow scope.

Here's what we learned early:

**One monolithic agent can't do everything well.** A single agent asked to review code, triage issues, hunt bugs, *and* generate ideas will do all of them poorly. Specialization wins. We'd rather have 40 focused agents than 1 confused generalist.

**Silence is better than noise.** Most of our agents are coached to stay quiet when there's nothing to report. Bug Hunter runs every day. Most days it finds nothing — and that's the goal. A healthy codebase is a success, not a missed opportunity to file an issue. An agent that files speculative findings is worse than one that stays silent.

**Evidence over opinions.** Every finding must include a file path, a line number, reproduction steps. No hand-waving. No "consider refactoring this." Concrete, actionable, verifiable.

**Humans stay in the loop.** Agents can file issues, post reviews, and open PRs — but they do it through guarded safe-output tools that enforce structure and prevent runaway mutations. Skip labels let your team flag false positives. The `/ai` command lets humans invoke agents on demand. Review-before-merge is still the norm.

**This is an experiment.** We're learning what works and sharing it openly. Some agents earn their keep every day. Others we've tuned, retired, or replaced. The factory evolves.

## Meet the Crew

We've organized the agents into squads based on what they do. Each squad has its own story — here's the cast:

**[The Reviewers](meet-the-reviewers.md)** — PR Review, Mention in PR, Update PR Body, and Docs PR Review. They're the first responders on every pull request. PR Review posts file-by-file severity-ranked comments. If it finds real issues, it dispatches itself to go fix them.

**[The Detectives](meet-the-detectives.md)** — PR Actions Detective, Branch Actions Detective, and PR Buildkite Detective. CI is red and the logs are 4,000 lines of noise. The Detectives find the one line that matters and tell you what went wrong.

**[The Issue Squad](meet-the-issue-squad.md)** — Issue Triage, Duplicate Issue Detector, Stale Issues, Plan, and Deep Research. A new issue lands and within seconds it's labeled, prioritized, and checked against every existing issue for duplicates. Deep Research is the one agent that breaks the mold — it uses Google Gemini instead of Copilot for extended investigation.

**[The Quality Crew](meet-the-quality-crew.md)** — Bug Hunter, Bug Exterminator, Flaky Test Investigator, Code Duplication Detector, Refactor Opportunist, Text Auditor, and more. They form a spectrum from "find bugs" (reactive) to "prevent bugs" (proactive architecture analysis). Bug Hunter has the highest quality bar in the factory — mandatory local reproduction, concrete failure scenarios, evidence-based findings.

**[The Idea Machines](meet-the-idea-machines.md)** — Custom audit agents we built using the Scheduled Audit base workflow, each thinking from a different persona. An example of what you can build when you give a generic workflow a personality and a schedule.

**[The Smoke Testers](meet-the-smoke-testers.md)** — Custom audit agents that run Playwright tests every weekday morning. Another example of the base workflow pattern — silence unless something breaks.

**[The Watchdogs](meet-the-watchdogs.md)** — Breaking Change Detector, Performance Profiler, UX Design Patrol, and Release Update Check. They guard the things developers forget to check — undocumented API changes, performance regressions, design drift.

**[The Docs Patrol](meet-the-docs-patrol.md)** — Docs Patrol and Docs PR Review. Code changes. Docs don't. These agents make sure they stay in sync, scanning both internal README files and published Elastic documentation for staleness.

## Quick Start

Getting agents running on your repo takes three steps:

1. **Store a Copilot PAT** as `COPILOT_GITHUB_TOKEN` in your repo secrets
2. **Copy a workflow's `example.yml`** from the [gh-agent-workflows](https://github.com/elastic/ai-github-actions/tree/main/gh-agent-workflows) directory
3. **Customize** with `additional-instructions` and `setup-commands` for your project

That's it. Updates propagate automatically through the `v0` tag. See the [full setup docs](../../workflows/gh-agent-workflows.md) for details.

## What We're Learning

This welcome post is just the beginning. We're writing about what we've discovered running a factory of AI agents in production:

- **[A Day in the Factory](a-day-in-the-factory.md)** — The schedule as a narrative. What happens when the factory wakes up at 9 AM UTC and runs through its shifts until 5 PM.
- **[Silence Is Better Than Noise](silence-is-better-than-noise.md)** — Our design philosophy. Why we coach agents to stay quiet, why noop is success, and why 40 focused agents beat 1 confused generalist.
- **[Architecture Under the Hood](architecture-under-the-hood.md)** — How agents actually execute. The two-job pattern, prompt assembly pipeline, sandboxed execution, and the safe-output guardrail system.

## Join Us

The entire framework is open source. Every agent prompt, every workflow definition, every guardrail — it's all in the repo. We built this because we believe the best way to learn about agentic workflows is to run them at scale and share what happens.

Try an agent. File an issue if it misbehaves. Propose a new one. The factory is always hiring.

[Get started](../../workflows/gh-agent-workflows.md){ .md-button .md-button--primary }
[Browse the agents](../../workflows/gh-agent-workflows.md#available-workflows){ .md-button }
