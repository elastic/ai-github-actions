# GitHub Agent Workflows

This directory contains workflow templates and per-workflow documentation.

Full documentation and setup guides live in the docs site:
https://elastic.github.io/ai-github-actions/workflows/gh-agent-workflows/

Each workflow folder includes an `example.yml` trigger and a README covering inputs and safe outputs.

## Base Workflows

Two generic base workflows let you build custom detectors and fixers without writing a full workflow from scratch. Provide your domain-specific instructions via `additional-instructions`:

| Workflow | Role | Output |
| --- | --- | --- |
| [Scheduled Audit](scheduled-audit/) | Detect issues and file reports | `create-issue` |
| [Scheduled Fix](scheduled-fix/) | Fix reported issues | `create-pull-request` |

These pair together: a Scheduled Audit finds problems, a Scheduled Fix resolves them.

## Specialized Workflows

Pre-built workflows with domain-specific prompts. These import the same base fragments (`scheduled-audit.md` / `scheduled-fix.md`) and layer specialized instructions on top.

**Detectors** (file issues):
- [Bug Hunter](bug-hunter/) — find reproducible bugs
- [Text Auditor](text-auditor/) — find text quality issues
- [Code Duplication Detector](code-duplication-detector/) — find duplicate code
- [Breaking Change Detector](breaking-change-detector/) — find breaking changes
- [Docs Patrol](docs-patrol/) — detect stale documentation
- [Product Manager Impersonator](product-manager-impersonator/) — propose well-researched new feature ideas
- [Refactor Opportunist](refactor-opportunist/) — pitch proven refactors with partial implementations
- [Stale Issues Investigator](stale-issues-investigator/) — detect stale issues
- [Stale Issues Remediator](stale-issues-remediator/) — process and close stale issues
- [Test Coverage Detector](test-coverage-detector/) — find under-tested code paths
**Fixers** (create PRs):
- [Bug Exterminator](bug-exterminator/) — fix bug-hunter issues
- [Text Beautifier](text-beautifier/) — fix text-auditor issues
- [Code Duplication Fixer](code-duplication-fixer/) — fix code-duplication-detector issues
- [Test Improver](test-improver/) — fix test-coverage-detector issues

**Event-driven** (comment on PRs):
- [Dependency Review](dependency-review/) — analyze Dependabot/Renovate dependency update PRs across ecosystems (GitHub Actions, Go, npm, Python, Java, Buildkite)

**Research assistants**:
- [Deep Research](deep-research/) — issue-comment deep research with web search/fetch and optional PR creation

## Quick setup script

Run from the repository you want to configure:

````bash
curl -fsSL https://raw.githubusercontent.com/elastic/ai-github-actions/v0/scripts/quick-setup.sh \
  | bash -s --
````

This installs a recommended set of triggers, adds `agentics-maintenance.yml`, sets up
`COPILOT_GITHUB_TOKEN`, creates a setup branch, and opens a PR.

Default workflows:
- `pr-review`
- `issue-triage`
- `mention-in-issue`
- `mention-in-pr`
- `pr-actions-detective`

Use `--workflows` (comma-separated) to override the defaults, `--skip-secret` to set the
secret manually, `--continuous-improvement` to also install selected continuous improvement
workflows, or `--repo OWNER/REPO` when auto-detection is not available.

`--continuous-improvement` adds:
- `bug-hunter`
- `bug-exterminator`
- `code-simplifier`
- `docs-patrol`
- `newbie-contributor-patrol`
- `product-manager-impersonator`
- `refactor-opportunist`
- `small-problem-fixer`
- `stale-issues-investigator`
- `stale-issues-remediator`
- `test-coverage-detector`
- `test-improver`
- `breaking-change-detector`
- `code-duplication-detector`
- `update-pr-body`

## Elastic-specific Workflows

These workflows are tailored for Elastic's internal tooling, documentation platform, and infrastructure. They reference Elastic's published documentation on `elastic.co/docs`, Elastic's style guide and `applies_to` tag conventions, or Elastic-owned infrastructure (Buildkite CI, downstream repositories). Use these if you are working in an Elastic repository.

- [Docs PR Review (Elastic-specific)](estc-docs-pr-review/) — review docs for Elastic style guide, `applies_to` tags, and consistency with `elastic.co/docs`
- [PR Buildkite Detective (Elastic-specific)](estc-pr-buildkite-detective/) — diagnose Buildkite CI failures and recommend fixes
- [Docs Patrol External (Elastic-specific)](estc-docs-patrol-external/) — detect stale published Elastic documentation
- [Newbie Contributor Patrol External (Elastic-specific)](estc-newbie-contributor-patrol-external/) — cross-reference repo docs against published Elastic documentation
- [Downstream Health (Elastic-specific)](estc-downstream-health/) — monitor downstream Elastic repositories using AI workflows
- [Resource Not Accessible Detector (Elastic-specific)](estc-actions-resource-not-accessible-detector/) — detect `Resource not accessible by integration` CI errors and file one combined tracking issue
