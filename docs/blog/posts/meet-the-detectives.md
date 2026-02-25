---
date: 2026-02-07
authors:
  - billeaston
categories:
  - Meet the Agents
---

# Meet the Detectives

CI is red. The logs are 4,000 lines of webpack noise. Somewhere in there is the one line that matters. That's the job of the Detectives -- three agents whose entire purpose is to read failure logs so you don't have to.

<!-- more -->

This is the smallest squad in the factory, but don't let the headcount fool you. CI failures are one of the highest-friction problems in any engineering team. A red build stops merges, blocks deployments, and sends developers scrolling through log output they didn't write. The Detectives exist to short-circuit that loop: read the logs, find the root cause, and tell you what to do about it.

## [PR Actions Detective](../../workflows/gh-agent-workflows/pr-actions-detective.md) -- The PR Investigator

The PR Actions Detective fires when a GitHub Actions check fails on a pull request. It pulls the failure logs, reads through the noise, and posts a diagnosis directly on the PR -- what broke, why, and what to fix.

It runs on GitHub Copilot with gpt-5.3-codex, and it only triggers on PR check failures. That's a deliberate constraint. This agent isn't scanning every run or reviewing passing builds. It stays silent until something actually breaks, and then it shows up with a concrete recommendation. The goal is to catch issues before they ever reach main. A developer opens a PR, CI fails, and within minutes the Detective has already read the 4,000-line log and posted the relevant excerpt with an explanation.

## [Branch Actions Detective](../../workflows/gh-agent-workflows/branch-actions-detective.md) -- The Post-Merge Sentinel

Not every failure happens on a PR. Sometimes code passes all checks, gets merged, and then breaks main. Maybe it's a timing issue, a flaky dependency, or a merge conflict that the individual PR checks didn't catch. The Branch Actions Detective watches for exactly this.

It triggers on failed checks against the main or default branch -- but only when those failures aren't associated with any open PR. That distinction is important. If a PR is open and its checks fail, the PR Actions Detective handles it. The Branch Actions Detective picks up the failures that nobody owns: post-merge breakage on main that would otherwise sit unnoticed until someone runs into it manually. It reads the logs, diagnoses the root cause, and files its findings so the team can act.

## [PR Buildkite Detective](../../workflows/gh-agent-workflows/pr-buildkite-detective.md)

Not every team runs CI exclusively on GitHub Actions. The PR Buildkite Detective does the same job as the PR Actions Detective, but for Buildkite CI pipelines. It requires a `BUILDKITE_API_TOKEN` to access pipeline logs, and from there the workflow is the same: read the failure, diagnose it, and recommend a fix directly on the PR.

If your CI lives in Buildkite, this is how you get the same automated diagnosis coverage that the other Detectives provide for GitHub Actions.

## How They Work Together

These three agents form a complete CI diagnosis pipeline. PR Actions Detective catches failures before merge -- the first line of defense. Branch Actions Detective catches what slips through, monitoring main for post-merge breakage that no PR owns. PR Buildkite Detective extends the same coverage to teams running Buildkite pipelines.

Together, they cover the full lifecycle: pre-merge on GitHub Actions, post-merge on main, and pre-merge on Buildkite. No gap in the pipeline goes undiagnosed. When CI goes red, a Detective is already reading the logs.

## Try It

All three Detectives are available as reusable workflows. See the [setup docs](../../workflows/gh-agent-workflows.md) for how to add them to your repo. If you're new to the factory, start with the [welcome post](welcome-to-the-factory.md) for the full picture.
