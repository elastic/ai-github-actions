---
date: 2026-02-17
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Watchdogs

These agents guard the things developers forget to check.

<!-- more -->

We have all been there. A release goes out, and two weeks later someone discovers that a public API signature changed without a migration note, or that a rendering path got three times slower, or that the factory's own workflow pinnings drifted behind by four versions. These are not bugs in the traditional sense — they are the slow accumulation of things nobody was explicitly watching. The watchdogs exist to watch them.

## [Breaking Change Detector](../../workflows/gh-agent-workflows/breaking-change-detector.md)

This agent runs on a weekday schedule and scans for undocumented public breaking changes. It looks at API surface changes, removed exports, and altered function signatures — anything that downstream consumers rely on. The key word is "undocumented." We are not trying to prevent breaking changes; sometimes they are necessary. We are trying to prevent the kind where a consumer upgrades and discovers the breakage in production because nobody mentioned it in the changelog.

## [Performance Profiler](../../workflows/gh-agent-workflows/performance-profiler.md)

Also on a weekday schedule, the Performance Profiler identifies slow paths, memory issues, and rendering bottlenecks. Performance regressions are notoriously hard to catch in code review because they rarely look like bugs. A slightly larger data structure here, an extra re-render there — individually harmless, collectively brutal. This agent profiles the application and flags hotspots before they compound into user-facing slowness.

## [Release Update Check](../../workflows/gh-agent-workflows/release-update.md)

This one runs on a weekly schedule and does something a little meta: it keeps the factory itself up to date. It opens a PR that updates the pinned ai-github-actions workflow SHAs in downstream repositories and suggests any workflow configuration changes that come with the new version. Without this agent, teams would be running stale versions of the factory workflows indefinitely, missing improvements and bug fixes. It is the watchdog that watches the watchdogs.

## [UX Design Patrol](../../workflows/gh-agent-workflows/ux-design-patrol.md)

Running on a weekday schedule, the UX Design Patrol reviews UI components for design consistency, accessibility compliance, and adherence to established UX patterns. It catches the kind of drift that happens when multiple developers build features independently — slightly different button styles, inconsistent spacing, missing ARIA labels. Design systems help, but they do not enforce themselves. This agent does.

## [Information Architecture](../../workflows/gh-agent-workflows/information-architecture.md)

The Information Architecture agent evaluates whether the application's interface is logically organized, navigable, and consistent. It traces the component tree from the top-level layout, examining navigation structure, action placement, data presentation patterns, progressive disclosure, and empty states. It only files an issue when it finds a concrete, user-impacting IA problem — something a real user would likely get confused or frustrated by. Like the other watchdogs, most runs end with `noop`.

## [Downstream Health (Elastic-specific)](../../workflows/gh-agent-workflows/estc-downstream-health.md)

Running on a daily schedule, the Downstream Health agent monitors the overall quality of downstream repositories. It provides a regular pulse check on the repos that consume the factory's workflows and components, catching issues that might not surface in any single focused audit but become visible when you look at the repository holistically.

## How They Work Together

The watchdogs are not independent sentries -- they overlap intentionally. The Breaking Change Detector catches API-level regressions. The Performance Profiler catches runtime regressions. The UX Design Patrol catches visual and consistency drift. The Release Update Check keeps the tooling current so the other agents are always running the latest checks. And Downstream Health ties it all together with a broad quality signal across the repositories that depend on us. Information Architecture extends coverage into the domain of UI structure and navigation.

None of these agents replace human judgment. They surface the things humans would eventually notice — just weeks or months earlier, when fixing them is still cheap.

## Try It

All of these watchdog agents are built on the workflow library we ship as part of the AI Software Factory. You can configure and deploy them in your own repositories using the [GitHub Agent Workflows](../../workflows/gh-agent-workflows.md) documentation.

For the full picture of how the factory works, head back to [Welcome to the Factory](welcome-to-the-factory.md).
