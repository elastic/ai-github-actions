---
date: 2026-02-20
authors:
  - billeaston
categories:
  - Design
---

# A Day in the Factory

What does it look like when a repo runs the full Elastic AI Software Factory? We deployed the framework on our playground repository -- combining the named workflows that ship with ai-github-actions and a set of custom [Scheduled Audit](../../workflows/gh-agent-workflows/scheduled-audit.md) configurations (Ideas Man agents, Playwright smoke testers, and domain-specific analyzers). The result is over 30 agents running on a daily schedule, and from the outside it can look like chaos. But there is a rhythm to it.

<!-- more -->

This is the story of a Monday in that deployment, told hour by hour. All times are UTC. Some agents below are named workflows from the framework (Bug Hunter, PR Review, etc.). Others are custom configurations we built on the Scheduled Audit base (marked with *custom* in the schedule table). Your deployment will look different -- the point is the pattern, not the specific lineup.

The event-driven agents are always listening in the background, but the scheduled crew punches in at 9 AM sharp.

## The Morning Shift

> **9:00 AM** — The day begins with confidence checks. Smoke Welcome Flow fires first, walking through the most critical user journey in the product: can a new user land on the welcome screen and proceed? While that runs, Iterative Ideas Man wakes up and scans the codebase for small, incremental improvements — the kind of thing a senior engineer notices during a code review but never files a ticket for. Project Summary rounds out the hour by generating a concise snapshot of where the repository stands: open PRs, recent merges, issue velocity. It is the morning standup nobody has to attend.

> **10:00 AM** — The factory shifts to the connection dialog. Smoke Connection Dialog validates that users can open, interact with, and dismiss the connection UI without errors. Medium Ideas Man takes a wider lens than its iterative sibling, looking for medium-effort improvements that could meaningfully move the product forward. Product Manager Impersonator steps back even further and asks: if we were a PM looking at this repo for the first time, what would we prioritize? And Text Auditor combs through every user-facing string for typos, inconsistencies, and tone mismatches. Four agents, four completely different perspectives, all running in parallel.

> **11:00 AM** — Security hour. Smoke Auth Tab Switch tests the authentication tab-switching flow — a subtle area where state bugs love to hide. Security Ideas Man reviews the codebase through a security lens, looking for hardcoded secrets, overly permissive configurations, and missing input validation. Bug Hunter goes hunting. It reads the code, reasons about edge cases, and files issues only when it finds concrete, reproducible bugs. If it finds nothing, that is a good sign — silence means health.

## The Afternoon Push

> **12:00 PM** — Smoke Connect Button Enablement checks that the connect button enables and disables correctly based on form state. Observability Ideas Man looks for gaps in logging, metrics, and tracing. Are we capturing the signals we need to debug production issues? Code Duplication Detector scans for copy-pasted logic that should be extracted into shared utilities. It is not pedantic about it — it looks for meaningful duplication that creates real maintenance burden.

> **1:00 PM** — Smoke Reset Visibility validates the reset button's show/hide behavior. Vector Search Ideas Man focuses specifically on our vector search implementation, proposing improvements to indexing, query performance, and relevance tuning. Framework Best Practices audits the codebase against the conventions and patterns recommended by the frameworks we use — React, Node, whatever the repo is built on.

> **2:00 PM** — The investigative hour. Flaky Test Investigator digs into tests that sometimes pass and sometimes fail, the kind of tests that erode confidence in CI and train developers to ignore red builds. Performance Profiler looks for obvious performance bottlenecks: unnecessary re-renders, N+1 queries, unbounded loops. Breaking Change Detector reviews recent changes and flags anything that could break downstream consumers or public APIs.

## The Late Shift

> **3:00 PM** — Code quality time. Code Simplifier looks for logic that can be expressed more clearly — overly nested conditionals, unnecessary abstractions, functions doing too many things. Refactor Opportunist identifies larger structural improvements: modules that should be split, interfaces that should be unified, dead code that should be removed. Docs Patrol checks that documentation stays in sync with the code it describes.

> **4:00 PM** — Community and hygiene. Newbie Contributor Patrol scans for issues that would make good first contributions and ensures they are labeled and well-described. Autonomy Atomicity Analyzer checks that our agents and workflows are properly decomposed — each one doing one thing well. Stale Issues sweeps through the issue tracker and flags anything that has gone cold.

> **5:00 PM** — The weekly crew clocks in on their designated days. Information Architecture reviews the overall structure of the documentation site. UX Design Patrol evaluates the product from a design perspective, looking for inconsistencies and usability issues. Small Problem Fixer picks up trivial issues — typos, missing semicolons, outdated comments — and just fixes them directly. Test Improver reviews the test suite for gaps, weak assertions, and missing edge cases.

## After Hours

And that is just Monday. The event-driven agents — PR Review, the Detectives, Issue Triage — never sleep. They fire on every trigger, day or night.

When a pull request opens, PR Review reads every line of the diff and leaves a thorough review. PR Actions Detective and Branch Actions Detective watch for CI failures and help diagnose what went wrong. Issue Triage categorizes and labels new issues as they arrive. Duplicate Issue Detector catches issues that have already been filed. Update PR Body keeps PR descriptions accurate as the code evolves.

Then there are the on-demand agents, invoked by humans when they need help: `/ai` in a PR or issue for interactive assistance, `/plan` for implementation planning, `/research` for deep technical research, and `/docs-review` for documentation-specific PR review. These wait patiently until called.

The factory is not about replacing engineers. It is about running the tedious, repetitive, easy-to-forget work on a schedule so that humans can focus on the hard problems. If you want to understand the philosophy behind these choices, read [the design principles post](silence-is-better-than-noise.md). And if you are just arriving, start with [Welcome to the Factory](welcome-to-the-factory.md).

## Quick Reference Schedule

All times UTC, weekdays unless noted.

| Time | Agents |
|------|--------|
| 9:00 AM | Smoke Welcome Flow *(custom)*, Iterative Ideas Man *(custom)*, Project Summary |
| 10:00 AM | Smoke Connection Dialog *(custom)*, Medium Ideas Man *(custom)*, Product Manager Impersonator, Text Auditor |
| 11:00 AM | Smoke Auth Tab Switch *(custom)*, Security Ideas Man *(custom)*, Bug Hunter |
| 12:00 PM | Smoke Connect Button Enablement *(custom)*, Observability Ideas Man *(custom)*, Code Duplication Detector |
| 1:00 PM | Smoke Reset Visibility *(custom)*, Vector Search Ideas Man *(custom)*, Framework Best Practices *(custom)* |
| 2:00 PM | Flaky Test Investigator, Performance Profiler, Breaking Change Detector |
| 3:00 PM | Code Simplifier, Refactor Opportunist, Docs Patrol |
| 4:00 PM | Newbie Contributor Patrol, Autonomy Atomicity Analyzer *(custom)*, Stale Issues |
| 5:00 PM | Information Architecture *(custom)*, UX Design Patrol, Small Problem Fixer, Test Improver *(weekly)* |

**Event-driven (anytime):** PR Review, PR Actions Detective, Branch Actions Detective, Issue Triage, Duplicate Issue Detector, Update PR Body

**On-demand:** Mention in PR (`/ai`), Mention in Issue (`/ai`), Plan (`/plan`), Deep Research (`/research`), Docs PR Review (`/docs-review`)
