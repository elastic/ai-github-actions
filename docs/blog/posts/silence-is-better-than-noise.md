---
date: 2026-02-21
authors:
  - billeaston
categories:
  - Design
---

# Silence Is Better Than Noise

We have seen what happens when teams bolt AI onto their workflows without guardrails. You get a firehose of speculative issues, vague suggestions, and noisy PR comments that train developers to ignore everything the bot says. The Elastic AI Software Factory is built on the opposite philosophy: an agent that has nothing useful to say should say nothing at all.

<!-- more -->

These are the design principles we use to evaluate every agent in the factory. They are not aspirational — they are enforced in prompts, tested in practice, and refined every week. If an agent violates one of these principles, we fix the agent or we turn it off.

## Silence over Noise

This is the first principle because it is the most important. An agent that files a speculative issue is worse than one that stays quiet. Speculation erodes trust. Once a developer learns to dismiss an agent's output, that agent is dead — even when it eventually finds something real.

Most of our agents are explicitly coached to report nothing when there is nothing to report. Bug Hunter runs daily. On a good day, it finds zero bugs and files zero issues. That is not a failure. That is the system working. A quiet Bug Hunter means the codebase is healthy. We would rather have an agent that catches one real bug per week than one that files five "maybe this is a problem?" issues per day.

The same goes for Code Duplication Detector, Security Ideas Man, and every other analytical agent. They are tuned for precision over recall. Missing a minor issue is acceptable. Filing a false positive is not.

## Evidence over Opinions

Every finding must include a file path, a line number, and reproduction steps where applicable. No hand-waving. No "consider refactoring this module." No "this could potentially be a performance issue."

We want concrete, actionable, verifiable output. If an agent says there is a bug, it should point to the exact line, explain what the expected behavior is, what the actual behavior is, and how to reproduce it. If an agent suggests a refactor, it should show the before and after. If it cannot do that, it should not file the issue.

This principle exists because vague suggestions create work without creating value. An engineer who receives a vague suggestion has to investigate whether it is even real before they can act on it. That investigation time is a hidden cost that compounds across dozens of agents and hundreds of issues.

## Noop Is Success

This follows directly from the first two principles but it is worth stating explicitly. The goal of the factory is a quiet dashboard. If Bug Hunter finds nothing, good. If all smoke tests pass, good. If Security Ideas Man has no findings, good.

We do not measure agent value by output volume. We measure it by signal quality. An agent that runs a thousand times and produces ten high-value findings is worth more than one that runs a thousand times and produces five hundred mediocre ones. The factory's success metric is not "how many issues did we file" but "how many issues did we file that a human acted on."

## Humans Stay in the Loop

Agents in the factory can file issues and open pull requests, but humans decide what ships. This is non-negotiable.

We enforce this at multiple levels. Skip labels let developers tell agents to leave specific code alone. The `/ai` command gives humans explicit control over when to invoke an agent in a PR or issue. Review-before-merge means no agent PR lands without a human approving it. And the safe-output tools that agents use to interact with GitHub enforce structured output formats and prevent runaway mutations — an agent cannot accidentally close every open issue or force-push to main.

This is not because we do not trust the agents. It is because we trust the process. Human review is the final quality gate, and removing it would undermine every other principle on this list.

## Specialization over Generalization

We run over 40 agents. That sounds like a lot until you understand why: 40 focused agents beat one confused generalist every time.

Each agent has a narrow scope and a clear mission. Bug Hunter hunts bugs. Flaky Test Investigator investigates flaky tests. Code Simplifier simplifies code. They do not overlap, and they do not try to be clever outside their lane.

This is why we have separate Bug Hunter and Flaky Test Investigator agents instead of one "code quality bot." A single agent trying to find bugs, diagnose flaky tests, detect duplication, audit security, and suggest refactors will do all of those things poorly. Specialization lets us tune each agent's prompt, intensity, and evaluation criteria independently. It lets us turn off one agent without affecting the others. And it makes failures easy to diagnose — when something goes wrong, you know exactly which agent did it and why.

## Intensity Is Configurable

Not every repository wants the same level of scrutiny. PR Review runs at aggressive intensity by default because we believe thorough code review is worth the noise. But you can tune it down. Every agent accepts `additional-instructions` as an input, which lets you customize the agent's behavior for your specific repo. You can tell Bug Hunter to ignore a particular directory, or tell Text Auditor to use British English, or tell Security Ideas Man to focus on a specific threat model.

This configurability is what makes the factory work across different teams with different standards. The defaults are opinionated, but they are not locked in.

## The Meta-Agent Pattern

Here is where it gets interesting. One of our agents — Agent Suggestions — watches the repository and proposes new agents. It looks at the kinds of issues that keep recurring, the patterns in PR review feedback, and the gaps in test coverage, and it suggests new specialized agents that could address those patterns.

Agents improving agents. The factory evolves itself. We still review and approve every new agent (humans in the loop, always), but the suggestions are often surprisingly good. Some of our best agents started as Agent Suggestions proposals.

---

These principles are not theoretical. They are the result of months of running agents in production, watching what works, and — more importantly — watching what fails. If you want to see these principles in action, read [A Day in the Factory](a-day-in-the-factory.md) for the daily schedule, or start from the beginning with [Welcome to the Factory](welcome-to-the-factory.md).
