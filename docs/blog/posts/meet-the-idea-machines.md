---
date: 2026-02-13
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Idea Machines

What if your repo generated its own feature backlog every morning? Not vague "we should consider" suggestions from a brainstorming doc nobody reads, but concrete, codebase-grounded feature proposals filed as issues -- five every day, each from a different domain expert. That's what the Idea Machines do.

<!-- more -->

The Idea Machines are all instances of the [Product Manager Impersonator](../../workflows/gh-agent-workflows/product-manager-impersonator.md) workflow, configured with different `persona` and `idea-size` inputs. You run the same workflow multiple times in a single trigger file — each job gets its own persona, scope, and title prefix.

Here's what we built for our playground repo. You can build your own set for any domain.

## Iterative Ideas Man -- The Quick Win Spotter

The Iterative Ideas Man fires at 9 AM UTC every day and files one small, iterative feature idea. Its persona is an enthusiastic product thinker who's done the research and genuinely believes each idea "won't be that hard." Every idea includes a section explaining why the effort is modest, grounded in actual codebase data points -- specific files, existing patterns, APIs already in use.

These are the ideas that unblock momentum. A missing filter on a list view. A config option that three users have asked about. A small UX improvement that leverages a component you already built. Issue prefix: `[idea]`.

## Medium Ideas Man -- The Sprint Scoper

One hour later, at 10 AM UTC, the Medium Ideas Man files a feature proposal scoped to a 1-2 sprint effort. Where the Iterative Ideas Man targets afternoon wins, this agent thinks in terms of planned work. Its persona is a pragmatic product thinker -- it includes realistic implementation outlines, effort estimates, and a breakdown of what needs to change.

This is the agent that populates the "next sprint" column. Each idea still includes "why it won't be that hard," but here "not that hard" means "achievable in a focused sprint, not a quarter." Issue prefix: `[medium idea]`.

## Security Ideas Man -- The SOC Analyst

At 11 AM UTC, the Security Ideas Man brings the perspective of a seasoned threat-hunter and SOC engineer. Its ideas focus on security workflows: threat hunting interfaces, alert triage improvements, IOC investigation tools, and detection engineering features. This isn't a vulnerability scanner -- it's a product thinker who thinks in terms of adversary behavior, MITRE ATT&CK coverage, and analyst friction.

Security features often get deprioritized in general planning. A product team might never propose a bulk IOC lookup workflow or a detection rule testing harness, but a SOC analyst would ask for it in the first week. The Security Ideas Man brings that voice daily. Issue prefix: `[security idea]`.

## Observability Ideas Man -- The SRE

At 12 PM UTC, the Observability Ideas Man thinks like a seasoned SRE and platform engineer who lives in logs, metrics, and distributed traces. Its ideas target the workflows on-call engineers actually use: log analysis, metric aggregation, distributed tracing, and anomaly investigation.

It proposes features that reduce mean-time-to-diagnosis: better correlation views, smarter log parsing, trace-to-metric linkage, anomaly detection that surfaces the signal before a human has to go hunting. Issue prefix: `[observability idea]`.

## Vector Search Ideas Man -- The Search Engineer

The final Idea Machine fires at 1 PM UTC, thinking like a search engineer and AI product builder. Its domain is relevance tuning, semantic and hybrid search, embedding inspection, and RAG pipeline improvements. Search quality always has another improvement to make -- a better reranking strategy, a more transparent relevance explanation, a tighter feedback loop between user behavior and index tuning. The Vector Search Ideas Man proposes those improvements daily, grounded in your actual search implementation. Issue prefix: `[search idea]`.

## The Daily Briefing

By 1 PM UTC every day, five fresh feature proposals have landed in your issue tracker. One quick win from the product thinker. One sprint-scoped project from the planner. One security workflow from the SOC analyst. One observability improvement from the SRE. One search enhancement from the search engineer. Five perspectives, each grounded in your actual codebase, each with a concrete implementation outline.

Every agent checks for duplicate ideas before filing. They review existing issues to make sure they're not proposing something already suggested or in progress. Nobody wants a backlog full of repeated proposals.

The result is a self-generating feature backlog that represents perspectives your team might not have on any given day. You don't have to act on every idea -- most teams cherry-pick the ones that resonate -- but you never run out of well-reasoned things to build.

## Build Your Own

Every Ideas Man agent is a [Product Manager Impersonator](../../workflows/gh-agent-workflows/product-manager-impersonator.md) job with its own `persona`, `idea-size`, and `title-prefix`. You're not limited to these five personas. Need a "Data Pipeline Ideas Man" or a "Mobile UX Ideas Man"? Add another job to your trigger file with a new persona prompt and you're running. See the [Product Manager Impersonator README](../../workflows/gh-agent-workflows/product-manager-impersonator.md) for a multi-persona example.

See the [workflow docs](../../workflows/gh-agent-workflows.md) for setup instructions and base workflow details. If you're new to the factory, start with the [welcome post](welcome-to-the-factory.md) for the full picture.
