# Agent Context

This page documents what context an agent receives when working in a repository that uses `ai-github-actions`. Understanding this helps you write effective `AGENTS.md` files and `additional-instructions` inputs.

---

## Copilot Coding Agent

The [Copilot Coding Agent](https://docs.github.com/en/copilot/using-github-copilot/coding-agent) reads `.github/agents/copilot-coding-agent.md` if present. This file contains system instructions that shape the agent's behavior for every task in the repository.

In addition, the **Copilot Coding Agent automatically reads `AGENTS.md`** (at the repository root) and includes its contents in the agent's context. This is read once at startup and requires no explicit call — it is automatic.

### Context received for each task

| Source | Content | Automatic? |
| --- | --- | --- |
| `.github/agents/copilot-coding-agent.md` | System-level instructions for the agent | Yes |
| `AGENTS.md` (root) | Repository coding guidelines, conventions, and cross-references | Yes |
| Task / problem statement | Issue title, body, and comments (for issue-triggered tasks) | Yes |
| Repository checkout | Full local clone of the repo (files, history) | Yes |

### What this repository's `AGENTS.md` contains

The `AGENTS.md` at the root of `ai-github-actions` currently reads:

```markdown
# AI GitHub Actions

@README.md
@DEVELOPING.md

## GitHub Agent Workflows

See ./gh-agent-workflows

## Claude Workflows (Composite Actions)

See ./claude-workflows
```

The `@README.md` and `@DEVELOPING.md` references instruct the Copilot Coding Agent to inline the contents of those files, so the agent receives:

- The repository overview from `README.md`
- The full developer guide from `DEVELOPING.md` (repo structure, how to compile and lint, how to add workflows)

---

## GitHub Agent Workflows (gh-aw)

For [`gh-aw`-based workflows](workflows/gh-agent-workflows.md) (e.g., `gh-aw-mention-in-issue`, `gh-aw-pr-review`), agent context is assembled differently — the agent runs ephemerally inside a GitHub Actions job and must fetch its context at runtime.

### How `generate_agents_md` works

Every `gh-aw` workflow that imports `gh-aw-fragments/elastic-tools.md` has access to the **`generate_agents_md`** MCP tool. Step 1 of those workflow prompts instructs the agent to call this tool:

> Call `generate_agents_md` to get the repository's coding guidelines and conventions. If this fails, continue without it.

The tool contacts `https://agents-md-generator.fastmcp.app/mcp` and returns a synthesized summary of the repository's `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, and related files. This is the gh-aw equivalent of the automatic `AGENTS.md` injection that the Copilot Coding Agent performs natively.

### Context received per workflow run

| Source | Content | How fetched |
| --- | --- | --- |
| `generate_agents_md` (MCP tool) | Synthesized summary of `AGENTS.md` and related files | Explicit call in Step 1 of the prompt |
| Workflow prompt | Task instructions, constraints, safe-output rules | Compiled into `.lock.yml` |
| GitHub event payload | Issue/PR number, title, comment text, actor | Injected via `${{ github.event.* }}` template variables |
| Repository checkout | Local workspace with files, git history | Checked out by the workflow runner |
| `additional-instructions` input | Repo-specific override instructions from the caller workflow | Appended to the end of the prompt |

### Example: mention-in-issue context log

When the `gh-aw-mention-in-issue` workflow fires on `@copilot fix the login bug`, the agent receives (in order):

1. **Workflow prompt** — the compiled `gh-aw-mention-in-issue.lock.yml` prompt containing:
   - Repository name (`${{ github.repository }}`)
   - Issue number and title
   - The triggering comment text
   - Step-by-step task instructions
   - Safe-output rules (what API calls are allowed)
2. **`generate_agents_md` result** — returned by the MCP server after reading `AGENTS.md` + related files
3. **Issue thread** — fetched via GitHub MCP toolset (`issue_read`)
4. **Codebase** — explored via `grep`, file reads, and bash commands in the workspace

---

## Writing an effective `AGENTS.md`

Because `AGENTS.md` is automatically read by both the Copilot Coding Agent and (via `generate_agents_md`) by gh-aw workflows, it is the single most impactful file for shaping agent behavior across all workflows.

Effective `AGENTS.md` files typically include:

- **Repository overview** — what the project does and how it is structured
- **Development commands** — how to build, lint, test (e.g. `make compile`, `make lint`)
- **Code style pointers** — links to `CODE_STYLE.md` or inline rules
- **Cross-references** — `@README.md`, `@DEVELOPING.md` to inline additional files

The `@filename` syntax (supported by the Copilot Coding Agent) causes the referenced file's content to be inlined into the context. Use it to avoid duplicating content between `README.md`, `DEVELOPING.md`, and `AGENTS.md`.
