![AI GitHub Actions Banner](assets/banner.png)

# AI GitHub Actions

*Drop-in AI agents for GitHub repos. They triage issues, review PRs, diagnose CI failures, and continuously improve your codebase — all through standard GitHub Actions. Get started with our 5 core workflows with more than 40 additional workflows available to use as needed.*

---

## Get Started in 60 Seconds

The agents use GitHub Copilot as their AI engine. You create a personal access token (PAT) so the workflows can authenticate.

**1. Create a Copilot PAT** — this link pre-fills the name, description, and scope:

[Create COPILOT_GITHUB_TOKEN →](https://github.com/settings/personal-access-tokens/new?name=COPILOT_GITHUB_TOKEN&description=GitHub+Agentic+Workflows+-+Copilot+engine+authentication&user_copilot_requests=read){ .md-button .md-button--primary }

Set the expiry to longer than the 30-day default (e.g., 90 days or 1 year).

**2. Store the secret and install the core workflows** — `cd` into the repo you want to configure and run:

```bash
printf '%s' 'YOUR_PAT_HERE' | gh secret set COPILOT_GITHUB_TOKEN

mkdir -p .github/workflows && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/issue-triage/example.yml \
  -o .github/workflows/trigger-issue-triage.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-issue/example.yml \
  -o .github/workflows/trigger-mention-in-issue.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/mention-in-pr/example.yml \
  -o .github/workflows/trigger-mention-in-pr.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-review/example.yml \
  -o .github/workflows/trigger-pr-review.yml && \
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/pr-actions-detective/example.yml \
  -o .github/workflows/trigger-pr-actions-detective.yml
```

**3. Commit and push.** That's it — you now have five agents working for you:

- **New issues** are automatically triaged, labeled, and given an implementation plan.
- **Pull requests** get AI code reviews with severity-ranked inline comments.
- **Failed CI checks** are diagnosed with root-cause analysis and fix suggestions.
- **Type `/ai` in any issue or PR** to ask for help, get code written, or push fixes.

See the [full setup docs](workflows/gh-agent-workflows.md) for secrets, inputs, and customization options.

---

## Core Workflows

These five workflows ship with the install command above:

| Workflow | Trigger | What it does |
| --- | --- | --- |
| **[Issue Triage](workflows/gh-agent-workflows/issue-triage.md)** | New issues | Investigate, label, and provide implementation plans |
| **[Mention in Issue](workflows/gh-agent-workflows/mention-in-issue.md)** | `/ai` in issues | Answer questions, debug, create PRs |
| **[Mention in PR](workflows/gh-agent-workflows/mention-in-pr.md)** | `/ai` in PRs | Review, fix code, push changes |
| **[PR Review](workflows/gh-agent-workflows/pr-review.md)** | PR opened / updated | AI code review with severity-ranked inline comments |
| **[PR Actions Detective](workflows/gh-agent-workflows/pr-actions-detective.md)** | Failed PR checks | Diagnose CI failures and recommend fixes |

---

## Repository Maintenance

Add-on workflows that keep your issues and PRs clean:

| Workflow | What it does |
| --- | --- |
| [Duplicate Issue Detector](workflows/gh-agent-workflows/duplicate-issue-detector.md) | Flag duplicate issues with links to originals |
| [Stale Issues](workflows/gh-agent-workflows/stale-issues.md) | Find resolved issues and manage their lifecycle |
| [Update PR Body](workflows/gh-agent-workflows/update-pr-body.md) | Auto-populate PR descriptions from diffs and linked issues |

??? tip "Install these workflows"

    `cd` into your repo and run:

    ```bash
    mkdir -p .github/workflows && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/duplicate-issue-detector/example.yml \
      -o .github/workflows/trigger-duplicate-issue-detector.yml && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/stale-issues-investigator/example.yml \
      -o .github/workflows/trigger-stale-issues-investigator.yml && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/update-pr-body/example.yml \
      -o .github/workflows/trigger-update-pr-body.yml
    ```

---

## Codebase Maintenance

Scheduled agents that continuously find and fix problems:

| Workflow | What it does |
| --- | --- |
| [Bug Hunting](workflows/gh-agent-workflows/bugs.md) | Find reproducible bugs and open PRs to fix them |
| [Code Duplication](workflows/gh-agent-workflows/code-duplication.md) | Detect duplicate code and consolidate it |
| [Test Coverage](workflows/gh-agent-workflows/test-coverage.md) | Find coverage gaps and add targeted tests |
| [Code Complexity](workflows/gh-agent-workflows/code-complexity.md) | Find overly complex code and file simplification reports |
| [Docs Patrol](workflows/gh-agent-workflows/docs-patrol-overview.md) | Catch stale documentation |

??? tip "Install these workflows"

    `cd` into your repo and run:

    ```bash
    mkdir -p .github/workflows && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/bug-hunter/example.yml \
      -o .github/workflows/trigger-bug-hunter.yml && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-duplication-detector/example.yml \
      -o .github/workflows/trigger-code-duplication-detector.yml && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/test-coverage-detector/example.yml \
      -o .github/workflows/trigger-test-coverage-detector.yml && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/code-simplifier/example.yml \
      -o .github/workflows/trigger-code-simplifier.yml && \
    curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/gh-agent-workflows/docs-patrol/example.yml \
      -o .github/workflows/trigger-docs-patrol.yml
    ```

[Browse all 40+ workflows →](workflows/gh-agent-workflows.md){ .md-button }

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
