---
date: 2026-02-14
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Smoke Testers

Five silent sentinels run every weekday morning. You never hear from them -- unless something breaks.

<!-- more -->

The smoke test agents don't ship as named workflows in the ai-github-actions framework. Like the [Idea Machines](meet-the-idea-machines.md), they're custom configurations we built on top of the [Scheduled Audit](../../workflows/gh-agent-workflows/scheduled-audit.md) base workflow -- each one given a specific Playwright test scenario to validate via `additional-instructions`. We're showing them here because they demonstrate a powerful pattern: using a generic audit workflow to run real E2E tests on a schedule, with zero-noise reporting.

Here's how we set them up for our playground app. They are Playwright-based, they run on a staggered schedule every weekday morning, and they validate the critical user journey: landing, connect, explore, reset. If every step works, you get silence. If something breaks, you get a GitHub issue.

## The Five Agents

**Smoke Welcome Flow** runs at 9 AM UTC. It validates the onboarding experience — is the landing page visible? Is the "Connect to Elasticsearch" call-to-action ready and clickable? This is the front door. If this fails, nothing else matters.

**Smoke Connection Dialog** fires at 10 AM UTC. It walks through the metrics flow: open the connection dialog, pick a real metric (`system.cpu.total.norm.pct`), and verify that the chart renders and save controls appear. This catches regressions in the connection and visualization pipeline.

**Smoke Auth Tab Switch** runs at 11 AM UTC. It validates the authentication UX by confirming that API key fields appear first, that switching to username/password works, and that switching back works too. Auth UX is one of those things that breaks silently when someone refactors a tab component, so we test it explicitly.

**Smoke Connect Button Enablement** kicks off at 12 PM UTC. This one validates the traces flow end-to-end: connect, run a search, click a trace row, view the service map, and pivot to Query Lab. It is the longest journey of the five and catches the widest range of integration issues.

**Smoke Reset Visibility** closes out the morning at 1 PM UTC. It validates the reset flow: the connect button should be disabled without a URL, enabled once a URL is entered, and after a mock connection the global Reset button should return the entire application to its landing state. This confirms that we clean up properly — no orphaned state, no stale UI.

## Why Stagger Them?

We spread the runs across the morning so failures are easier to isolate. If the 9 AM run passes but the 10 AM run fails, we know the issue is in the connection dialog, not the landing page. Staggering also keeps our CI runners from competing for resources.

## Build Your Own

Every smoke test agent is a [Scheduled Audit](../../workflows/gh-agent-workflows/scheduled-audit.md) workflow with a custom prompt that tells the agent which Playwright test to run and how to report failures. You can build the same thing for any app with an E2E test suite -- just write the `additional-instructions` that describe the scenario and the commands to run.

See the [workflow docs](../../workflows/gh-agent-workflows.md) for the base workflow setup. If you're new to the factory, start with the [welcome post](welcome-to-the-factory.md) for the full picture.
