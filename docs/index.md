![AI GitHub Actions Banner](assets/banner.png)

# AI GitHub Actions

*40+ AI agents. Zero new tabs to monitor. Your repo (almost) runs itself.*

---

## Get Started in 60 Seconds

**1. Create a Copilot PAT** (the link pre-fills name, description, and scope):

[Create COPILOT_GITHUB_TOKEN →](https://github.com/settings/personal-access-tokens/new?name=COPILOT_GITHUB_TOKEN&description=GitHub+Agentic+Workflows+-+Copilot+engine+authentication&user_copilot_requests=read){ .md-button .md-button--primary }

Set the expiry to longer than the 30-day default (e.g., 90 days or 1 year).

**2. Store the secret and run the setup script** from the repository you want to configure (requires `gh`, `git`, and `curl`):

```bash
printf '%s' 'YOUR_PAT_HERE' | gh secret set COPILOT_GITHUB_TOKEN
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
```

This installs the core workflows, sets up `agentics-maintenance.yml`, creates a branch, and opens a PR. Use `--continuous-improvement` to also install codebase maintenance workflows.

Or set up manually — see the [full setup docs](workflows/gh-agent-workflows.md).

---

## Core Workflows

These four workflows are the foundation — install them first and you'll cover most day-to-day development needs:

| Workflow | Trigger | What it does |
| --- | --- | --- |
| **[Issue Triage](workflows/gh-agent-workflows/issue-triage.md)** | New issues | Investigate, label, and provide implementation plans |
| **[Mention in Issue](workflows/gh-agent-workflows/mention-in-issue.md)** | `/ai` in issues | Answer questions, debug, create PRs |
| **[Mention in PR](workflows/gh-agent-workflows/mention-in-pr.md)** | `/ai` in PRs | Review, fix code, push changes |
| **[PR Review](workflows/gh-agent-workflows/pr-review.md)** | PR opened / updated | AI code review with severity-ranked inline comments |

---

## Repository Maintenance

Keep your issues and PRs clean and well-organized:

| Workflow | What it does |
| --- | --- |
| [Duplicate Issue Detector](workflows/gh-agent-workflows/duplicate-issue-detector.md) | Flag duplicate issues with links to originals |
| [Stale Issues](workflows/gh-agent-workflows/stale-issues.md) | Find resolved issues and manage their lifecycle |
| [Update PR Body](workflows/gh-agent-workflows/update-pr-body.md) | Auto-populate PR descriptions from diffs and linked issues |
| [PR Actions Detective](workflows/gh-agent-workflows/pr-actions-detective.md) | Diagnose CI failures and recommend fixes |

---

## Codebase Maintenance

Scheduled agents that continuously improve your codebase:

| Workflow | What it does |
| --- | --- |
| [Bug Hunting](workflows/gh-agent-workflows/bugs.md) | Find and fix reproducible bugs |
| [Code Duplication](workflows/gh-agent-workflows/code-duplication.md) | Detect and consolidate duplicate code |
| [Test Coverage](workflows/gh-agent-workflows/test-coverage.md) | Find coverage gaps and add targeted tests |
| [Code Complexity](workflows/gh-agent-workflows/code-complexity.md) | Find overly complex code and file simplification reports |
| [Docs Patrol](workflows/gh-agent-workflows/docs-patrol-overview.md) | Catch stale documentation |

[Browse all workflows →](workflows/gh-agent-workflows.md){ .md-button }

---

## Meet the Crew

<div class="grid cards" markdown>

-   **[The Reviewers](blog/posts/meet-the-reviewers.md)**

    ---

    PR Review, Mention in PR, Update PR Body. File-by-file severity-ranked code reviews on every pull request — and they fix what they find.

-   **[The Detectives](blog/posts/meet-the-detectives.md)**

    ---

    PR Actions Detective, Branch Actions Detective. CI is red and the logs are noise. The Detectives find the line that matters.

-   **[The Quality Crew](blog/posts/meet-the-quality-crew.md)**

    ---

    Bug Hunter, Flaky Test Investigator, Code Duplication Detector. From finding bugs to preventing them — the full quality spectrum.

-   **[The Idea Machines](blog/posts/meet-the-idea-machines.md)**

    ---

    Product Manager Impersonator, configured with different personas. Daily feature proposals from an iterative thinker, an SRE, a security analyst, and more.

-   **[The Issue Squad](blog/posts/meet-the-issue-squad.md)**

    ---

    Issue Triage, Duplicate Detector, Deep Research. New issues are labeled, prioritized, and deduplicated within seconds.

-   **[The Watchdogs](blog/posts/meet-the-watchdogs.md)**

    ---

    Breaking Change Detector, Performance Profiler, UX Design Patrol, Information Architecture. They guard the things developers forget to check.

</div>

[Browse all blog posts](blog/index.md){ .md-button }
