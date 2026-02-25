---
date: 2026-02-12
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Quality Crew

Most agents find things. The Bug Hunter is coached to find *nothing* -- and considers that a success. Its job is to hunt for reproducible, user-impacting bugs every single weekday. Most days it comes back empty-handed, and that's the best possible outcome. A healthy codebase doesn't need a bug report. The Quality Crew is built around that philosophy: find real problems, fix them concretely, and stay silent when there's nothing worth saying.

<!-- more -->

This is the largest squad in the factory. Some of these agents hunt for bugs. Others clean up code structure. A few operate at the architecture level, catching patterns that cause problems before they ever manifest as bugs. Together they form a spectrum from reactive ("find what's broken") to proactive ("prevent what could break").

## [Bug Hunter](../../workflows/gh-agent-workflows/bug-hunter.md) -- The Perfectionist

Bug Hunter has the highest quality bar of any agent in the factory. It doesn't file speculative concerns or suggest that something "might" be a problem. Every finding must include a concrete failure scenario, a file path, reproduction steps, and evidence from the actual code. If it can't reproduce the bug locally, it doesn't report it.

That bar is intentional. We learned early that a bug-hunting agent filing noisy, low-confidence reports is worse than no agent at all. Developers stop reading. Trust erodes. Bug Hunter earns its credibility by staying quiet when it isn't certain. It runs every weekday, scans for user-impacting bugs, and most days finds nothing. That silence means the codebase is healthy.

When Bug Hunter does find something, it's real. And that's where its partner comes in.

## [Bug Exterminator](../../workflows/gh-agent-workflows/bug-exterminator.md) -- The Closer

Bug Exterminator picks up Bug Hunter's findings and creates pull requests to fix them. This is the detector/fixer pair pattern we use across the factory: one agent finds, another agent fixes. Bug Hunter doesn't worry about writing patches. Bug Exterminator doesn't worry about whether the finding is valid -- it trusts the quality bar that Bug Hunter already enforced.

## [Flaky Test Investigator](../../workflows/gh-agent-workflows/flaky-test-investigator.md) -- The Pattern Matcher

Flaky tests corrode confidence in your entire test suite. The Flaky Test Investigator doesn't just look at one failure -- it looks for patterns across multiple CI runs. A test that failed once might be a cosmic ray. A test that failed three times in the last week with the same stack trace is a real problem.

It runs on a weekday schedule and also triggers on failed CI runs. When it finds a pattern, it files a root-cause-first triage report: here's the test, here's the pattern, here's why it's flaky. That framing matters. Developers don't need to know a test is flaky -- they already know. They need to know *why*.

## [Code Duplication Detector](../../workflows/gh-agent-workflows/code-duplication-detector.md) and [Code Duplication Fixer](../../workflows/gh-agent-workflows/code-duplication-fixer.md)

Another detector/fixer pair. The Code Duplication Detector scans for duplicate and clustered code -- not just exact copies, but structurally similar blocks doing the same thing in slightly different ways. The Code Duplication Fixer takes those findings and creates PRs that consolidate into shared abstractions.

Unintentional duplication is a maintenance burden that compounds. When three components each implement their own validation logic, a bug fix in one leaves the other two broken. These agents catch that drift before it causes real damage.

## [Refactor Opportunist](../../workflows/gh-agent-workflows/refactor-opportunist.md) and [Code Simplifier](../../workflows/gh-agent-workflows/code-simplifier.md)

These two agents work the middle of the quality spectrum. They aren't hunting for bugs -- they're hunting for code that works but could work better.

The Refactor Opportunist runs on a weekday schedule, scanning for functions that have grown too large, abstractions that no longer match their usage, and patterns that have drifted from codebase conventions. The Code Simplifier takes a tighter focus, targeting overcomplicated code with high-confidence simplifications. Neither agent touches anything it isn't confident about. A bad refactor is worse than no refactor.

## [Text Auditor](../../workflows/gh-agent-workflows/text-auditor.md) and [Text Beautifier](../../workflows/gh-agent-workflows/text-beautifier.md)

User-facing strings deserve the same care as code. The Text Auditor scans for grammar issues, unclear phrasing, and inconsistent terminology across all user-visible text. The Text Beautifier creates PRs to fix what the Auditor finds. Same detector/fixer pattern, applied to language instead of logic.

## Custom Quality Agents

The base workflows make it straightforward to build your own quality agents. In our playground repo we run two custom [Scheduled Audit](../../workflows/gh-agent-workflows/scheduled-audit.md) configurations that sit at the proactive end of the spectrum: a **Framework Best Practices** agent that checks whether you're using your libraries the way they were designed, and an **Autonomy Atomicity Analyzer** that finds structural patterns (god files, merge-conflict magnets, over-broad tests) that cause problems when multiple developers work in parallel. These aren't named workflows in the framework -- they're examples of what you can build with `additional-instructions`.

## The Quality Spectrum

Step back and look at this squad as a progression. Bug Hunter sits at the reactive end: find real bugs hurting users right now. Flaky Test Investigator moves upstream: find test infrastructure problems before they erode confidence. Code Duplication Detector shifts to structural issues: find patterns that will cause bugs eventually. Refactor Opportunist and Code Simplifier work at the architecture level: improve code so bugs are harder to introduce. And with custom audit agents, you can push even further into proactive territory -- preventing entire categories of problems by getting the design right.

Reactive to proactive. No single agent covers the whole spectrum, but together the Quality Crew covers every stage from "something is broken" to "let's make sure it never breaks."

## Try It

All of these agents are available as reusable workflows. See the [setup docs](../../workflows/gh-agent-workflows.md) for how to add them to your repo. If you're new to the factory, start with the [welcome post](welcome-to-the-factory.md) for the full picture.
