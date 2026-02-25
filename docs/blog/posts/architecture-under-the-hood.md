---
date: 2026-02-24
authors:
  - billeaston
categories:
  - Architecture
---

# Architecture Under the Hood

We have written about [what the factory does](welcome-to-the-factory.md) and [why we designed it this way](silence-is-better-than-noise.md). This post is for the people who want to know how it works — the compilation pipeline, the prompt assembly, the engine configuration, and the security model that keeps everything contained.

<!-- more -->

If you have looked at the repository and wondered why there are `.md` files that produce `.lock.yml` files, or why some agents have "sandboxed" and "no-sandbox" variants, this post will answer those questions.

## The Two-Job Pattern

Every agent in the factory is implemented as two separate GitHub Actions jobs.

The first is the **workflow** file. It lives in the repository as a Markdown file (for example, `gh-aw-bug-hunter.md`) and gets compiled by the `gh-aw` tool into a locked YAML file (`gh-aw-bug-hunter.lock.yml`). This compiled workflow contains the full agent logic — prompt, model configuration, tools, and execution steps. It triggers only on `workflow_call`, meaning it cannot run on its own. It must be invoked by something else.

That something else is the **trigger** file. This is a plain YAML file (for example, `bug-hunter.yml`) that defines the actual event triggers — a cron schedule, a pull request event, a workflow dispatch, whatever the agent needs. The trigger file calls the compiled workflow via `uses:` and passes any necessary inputs.

Why this split? Because it lets consumer repos adopt agents with minimal configuration. A consumer copies the trigger file, customizes the inputs (schedule, additional instructions, setup commands), and points `uses:` at the compiled workflow in this repository. When we update the agent logic, the consumer gets the update automatically through the `v0` tag. The consumer never has to touch the workflow internals.

## Prompt Assembly

The workflow files are not plain Markdown. They use YAML frontmatter to define metadata — the engine, model, tools, permissions, and inputs — followed by the prompt body in Markdown. The prompt body is what the agent actually reads and follows.

The key mechanism here is **fragment imports**. The `gh-aw-fragments/` directory contains shared prompt fragments that encode common behaviors. For example:

- **elastic-tools** — Defines which safe-output tools the agent has access to.
- **runtime-setup** — Runs setup commands (npm install, pip install, etc.) before the agent starts.
- **formatting** — Establishes output formatting conventions so all agents produce consistently structured results.
- **rigor** — Encodes the "evidence over opinions" principle: file paths, line numbers, reproduction steps required.
- **review-process** — Defines how PR review agents should structure their feedback, including severity levels and skip-label handling.

A workflow Markdown file imports these fragments with a simple directive, and the `gh-aw` compiler resolves the imports, inlines the fragment content, and produces the final `.lock.yml`. This means we can update a shared behavior — say, the formatting conventions — in one place and have it propagate to every agent on the next compilation.

## Engine Configuration

Most agents in the factory run on `engine: copilot` with `model: gpt-5.3-codex`. This is the default configuration and it handles the vast majority of use cases well — code analysis, issue filing, PR review, smoke testing.

Deep Research is the notable exception. It uses `engine: gemini` with `model: gemini-3-pro-preview`, which gives it access to a larger context window and different reasoning characteristics that are better suited for long-form research tasks.

The engine and model are configurable per workflow via inputs. If a consumer repo wants to run Bug Hunter on a different model, they can override it in their trigger file. We have not seen many teams do this yet, but the flexibility is there for when model capabilities diverge enough to make it worthwhile.

## Safe Output Tools

All GitHub API mutations — creating issues, opening pull requests, posting review comments, adding labels — go through structured **safe-output tools**. These are not arbitrary API calls. They are predefined tool interfaces that enforce output format and prevent runaway mutations.

The available tools include:

- `create-issue` — Files a new issue with a structured title, body, and labels.
- `create-pull-request` — Opens a PR with a diff, description, and branch name.
- `review-comment` — Posts an inline review comment on a specific file and line.
- `submit-review` — Submits a full PR review with approve, request-changes, or comment status.
- `add-comment` — Adds a comment to an issue or PR.

An agent cannot perform mutations outside of these tools. It cannot close issues, delete branches, merge PRs, or modify repository settings. This is a hard constraint, not a soft guideline. The tools are the guardrails.

## Sandboxed vs No-Sandbox

Some agents have two variants: a sandboxed version and a no-sandbox version. The most prominent examples are Mention in PR and Mention in Issue — the `/ai` command agents that respond to human requests in PRs and issues.

The sandboxed version runs in a restricted environment with limited network access and constrained filesystem permissions. This is the default for most use cases. The no-sandbox version lifts some of those restrictions for repos that need the agent to install dependencies, run test suites, or access internal services during its analysis.

The choice between sandboxed and no-sandbox is made at the trigger level. Consumer repos pick the variant that matches their security requirements.

## Standard Inputs

Every workflow in the factory accepts two standard inputs that give consumer repos control over agent behavior without forking the workflow.

**`additional-instructions`** is a free-text prompt that gets appended to the agent's system prompt. This is where you tell Bug Hunter to ignore your legacy directory, or tell PR Review to enforce your team's specific naming conventions, or tell Ideas Man to focus on performance improvements. It is the primary customization mechanism and it is surprisingly powerful — a few well-chosen sentences can dramatically change an agent's behavior.

**`setup-commands`** is a string of shell commands that run before the agent starts its analysis. This is for environment setup: `npm ci`, `pip install -r requirements.txt`, `make build`, or whatever your repo needs to be in a working state before an agent can reason about it. Agents that need to run tests or build the project use this to ensure the environment is ready.

## The Base Workflow Pattern

Not every agent is built from scratch. The factory includes two generic base workflows: **Scheduled Audit** and **Scheduled Fix**.

Scheduled Audit is a read-only base — it analyzes the codebase and files issues about what it finds. Scheduled Fix is a write base — it makes changes and opens pull requests. Specialized agents like Bug Hunter, Ideas Man, Code Duplication Detector, and dozens of others are built by providing domain-specific `additional-instructions` to one of these bases.

This means creating a new agent is often as simple as writing a new trigger file with a specific prompt. The compilation pipeline, tool access, output formatting, and execution logic are all inherited from the base workflow. This is how we got to 40+ agents without 40+ independent implementations.

## Network and Security

Agents run behind a firewall with a domain allowlist. They can reach GitHub APIs and the configured model endpoints, but they cannot make arbitrary network requests. This prevents prompt injection attacks from tricking an agent into exfiltrating code or credentials to an external server.

Access to the factory itself is gated behind the `copilot-requests` feature flag. Repos must be explicitly opted in before they can use any agent. Combined with the safe-output tools, the sandboxing options, and the human-in-the-loop review process, this creates a layered security model where no single failure can result in uncontrolled mutations to a repository.

---

That is the machinery. If you want to see what it produces in practice, read [A Day in the Factory](a-day-in-the-factory.md). If you want to understand the philosophy behind the design, read [Silence Is Better Than Noise](silence-is-better-than-noise.md). And if you are just getting started, begin with [Welcome to the Factory](welcome-to-the-factory.md).
