![AI GitHub Actions Banner](assets/banner.png)

# AI GitHub Actions

*40+ AI agents. Zero new tabs to monitor. Your repo (almost) runs itself.*

We built a fleet of specialized AI agents that review PRs, hunt bugs, triage issues, investigate CI failures, generate feature ideas, and audit your docs — all running as GitHub Actions. This is the Elastic AI Software Factory.

[Welcome to the Agent Factory](blog/posts/welcome-to-the-factory.md){ .md-button .md-button--primary }
[Quick Start](workflows/gh-agent-workflows.md){ .md-button }

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

---

## Quick Start

Run the quick setup script from the repository you want to configure (requires `gh`, `git`, and `curl`):

```bash
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
```

By default, this:

- Installs the starter set of workflow triggers
- Adds `agentics-maintenance.yml`
- Sets `COPILOT_GITHUB_TOKEN`
- Creates a branch, pushes it, and opens a PR

Use `--continuous-improvement` to also install selected continuous improvement workflows.

Or set up manually:

1. **Store a Copilot PAT** as `COPILOT_GITHUB_TOKEN` in your repo secrets
2. **Copy a workflow's `example.yml`** from [gh-agent-workflows/](https://github.com/elastic/ai-github-actions/tree/main/gh-agent-workflows)
3. **Customize** with `additional-instructions` and `setup-commands` for your project

Updates propagate automatically through the `v0` tag. See the [full setup docs](workflows/gh-agent-workflows.md) for the complete guide.

---

## Explore the Full Catalog

The complete reference for every agent — triggers, inputs, safe outputs, and installation instructions.

[Workflows Reference](workflows/gh-agent-workflows.md){ .md-button }
