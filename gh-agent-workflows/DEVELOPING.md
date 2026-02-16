# Developing GitHub Agent Workflows

## Architecture

```
gh-agent-workflows/
├── pr-review.md              # Shim: description + trigger + engine + single import
├── issue-triage.md
├── mention-in-issue.md
├── mention-in-pr.md
├── docs-drift.md             # Shim: imports scheduled-report-rwx.md + docs-specific instructions
└── gh-aw-fragments/          # Shared fragments
    ├── elastic-tools.md      # Elastic MCP servers + their network entries
    ├── formatting.md         # Response formatting rules
    ├── rigor.md              # Accuracy & evidence standards
    ├── mcp-pagination.md     # MCP token limit guidance
    └── safe-output-*.md      # Safe-output declarations + agent guidance

.github/workflows/
├── gh-aw-fragments -> ../../gh-agent-workflows/gh-aw-fragments  # symlink
├── gh-aw-workflows/          # Prompts
│   ├── pr-review-rwx.md      # PR review agent prompt
│   ├── issue-triage-rwx.md   # Issue triage agent prompt
│   ├── mention-in-pr-rwxp.md # Mention-in-PR agent prompt (with push)
│   ├── mention-in-issue-rwxp.md  # Mention-in-issue agent prompt (with push)
│   └── scheduled-report-rwx.md   # Reusable scheduled report prompt
├── pr-review.md              # Copied from gh-agent-workflows/ by scripts/dogfood.sh
├── issue-triage.md           # (shim copies needed for compilation)
├── ...
└── gh-aw-upgrade-check.md    # Internal-only scheduled check for gh-aw releases
```

**Shims** (`*.md` at the top level) are what consumers install via `gh aw add`. They contain the engine, trigger, permissions, concurrency, roles, description, and a single `imports:` entry. Everything else comes from imports.

**Prompts** (`.github/workflows/gh-aw-workflows/`) contain the agent instructions, `tools:`, `network:`, and `safe-outputs:`. Each prompt imports the shared fragments it needs. Filenames follow the pattern `<workflow>-<tier>.md` where the tier indicates the permission level:

- **`rwx`** — Read, write (workspace), execute (bash). No push, no PR creation.
- **`rwxp`** — Read, write, execute, push. Can create PRs or push to PR branches via safe-outputs.

The gh-aw compiler only supports 2-level import paths (`dir/file.md`), so prompts are flattened files (e.g., `gh-aw-workflows/pr-review-rwx.md`), not nested subdirectories. Adding a new tier is a new file with its own prompt and a new shim that imports it.

**Shared fragments** (`gh-agent-workflows/gh-aw-fragments/`) provide cross-workflow configuration and guidance. They are symlinked into `.github/workflows/gh-aw-fragments/` so the compiler can find them. No `on:` field — validated but never compiled standalone.

## Import Structure

Each shim imports one prompt, which nests the shared fragments:

```
shim (pr-review.md)
 └── gh-aw-workflows/pr-review-rwx.md      # agent instructions + tools + network + safe-outputs
      ├── gh-aw-fragments/elastic-tools.md  # Elastic MCP servers + network entries
      ├── gh-aw-fragments/formatting.md     # response formatting rules
      ├── gh-aw-fragments/rigor.md          # accuracy & evidence standards
      └── gh-aw-fragments/mcp-pagination.md # pagination best practices
```

**Reusable prompts** can be shared across multiple shims. The shim body (markdown after the frontmatter `---`) is appended to the imported prompt, providing workflow-specific instructions. For example, `scheduled-report-rwx.md` is a generic report agent that multiple shims can import with different report assignments:

```
shim (docs-drift.md)                         # schedule + "check for docs drift" instructions
 └── gh-aw-workflows/scheduled-report-rwx.md # generic report framework
      ├── gh-aw-fragments/elastic-tools.md
      ├── gh-aw-fragments/formatting.md
      ├── gh-aw-fragments/rigor.md
      └── gh-aw-fragments/mcp-pagination.md

shim (gh-aw-upgrade-check.md)                # schedule + "check for gh-aw upgrades" instructions
 └── gh-aw-workflows/scheduled-report-rwx.md # same generic report framework
      └── ...
```

`gh-aw-upgrade-check` is an **internal-only** workflow — its shim lives directly in `.github/workflows/` (not in `gh-agent-workflows/`) so it is not installable via `gh aw add`. It runs on weekdays to check for new `gh-aw` releases and files issues tagged `[gh-aw-upgrade]`.

To add a new scheduled report, create a shim that imports `gh-aw-workflows/scheduled-report-rwx.md` and put the report-specific instructions in the shim body. No new prompt file needed.

### Shared fragments

Fragments live in `gh-agent-workflows/gh-aw-fragments/` and are symlinked into `.github/workflows/gh-aw-fragments/`. Prompts import them using the `gh-aw-fragments/` prefix.

| Fragment | Purpose |
| --- | --- |
| [gh-aw-fragments/elastic-tools.md](gh-aw-fragments/elastic-tools.md) | Elastic MCP servers (`agents-md-generator`, `public-code-search`) and their network entries |
| [gh-aw-fragments/formatting.md](gh-aw-fragments/formatting.md) | Response formatting rules |
| [gh-aw-fragments/rigor.md](gh-aw-fragments/rigor.md) | Accuracy & evidence standards |
| [gh-aw-fragments/mcp-pagination.md](gh-aw-fragments/mcp-pagination.md) | MCP token limit guidance and pagination patterns |
| [gh-aw-fragments/safe-output-add-comment.md](gh-aw-fragments/safe-output-add-comment.md) | Limitations for `add-comment` (body length, mentions, links) |
| [gh-aw-fragments/safe-output-review-comment.md](gh-aw-fragments/safe-output-review-comment.md) | Limitations for `create-pull-request-review-comment` (required fields, line rules) |
| [gh-aw-fragments/safe-output-submit-review.md](gh-aw-fragments/safe-output-submit-review.md) | Limitations for `submit-pull-request-review` (event types, own-PR restriction) |
| [gh-aw-fragments/safe-output-push-to-pr.md](gh-aw-fragments/safe-output-push-to-pr.md) | Limitations for `push-to-pull-request-branch` (patch size, fork restriction) |
| [gh-aw-fragments/safe-output-resolve-thread.md](gh-aw-fragments/safe-output-resolve-thread.md) | Limitations for `resolve-pull-request-review-thread` (thread ID format) |
| [gh-aw-fragments/safe-output-create-issue.md](gh-aw-fragments/safe-output-create-issue.md) | Limitations for `create-issue` (title, labels, assignees) |
| [gh-aw-fragments/safe-output-create-pr.md](gh-aw-fragments/safe-output-create-pr.md) | Limitations for `create-pull-request` (patch files/size, title) |

### Import rules

- The compiler only supports **2-level** import paths (`dir/file.md`). Paths with 3+ segments are interpreted as remote GitHub references. This is why prompts are flattened (e.g., `gh-aw-workflows/pr-review-rwx.md`, not `gh-aw-workflows/pr-review/rwx.md`).
- For **local compilation**, `make sync` (`scripts/dogfood.sh`) copies shims into `.github/workflows/` where the compiler resolves imports relative to `gh-aw-workflows/` and `gh-aw-fragments/`. For **remote consumers**, `gh aw add` rewrites imports to remote references relative to `.github/workflows/`.
- `engine:`, `on:`, `concurrency:`, `timeout-minutes:`, `strict:`, `roles:` are **not importable** — they must be in the shim.
- `safe-outputs:` in the main workflow override imported defaults. `tools:` merge additively.

## Local Development

### How compilation works

The `gh-aw` compiler processes `.md` files in `.github/workflows/`. `make sync` (which runs `scripts/dogfood.sh`) copies shims from `gh-agent-workflows/` and ensures the `gh-aw-fragments` symlink is real (see `core.symlinks` note below). Prompts live directly in `.github/workflows/gh-aw-workflows/`.

```
.github/workflows/
├── gh-aw-fragments -> ../../gh-agent-workflows/gh-aw-fragments  # symlink
├── gh-aw-workflows/              # prompts
│   ├── pr-review-rwx.md
│   ├── scheduled-report-rwx.md
│   └── ...
├── pr-review.md                  # copied from gh-agent-workflows/ by scripts/dogfood.sh
├── pr-review.lock.yml            # compiled output
├── docs-drift.md
├── docs-drift.lock.yml
├── gh-aw-upgrade-check.md        # repo-specific (not copied)
├── gh-aw-upgrade-check.lock.yml
└── ...
```

Copied shim files are committed to the repo so that remote compilation and `gh aw add` work. Each copy has a `# DO NOT EDIT` header comment identifying the canonical source.

> **Note:** This repo has `core.symlinks=false`, so git checks out the `gh-aw-fragments` symlink as a text file. `scripts/dogfood.sh` (run by `make sync` / `make compile`) converts it to a real symlink.

### Editing workflows

1. Edit shims in `gh-agent-workflows/`, prompts in `.github/workflows/gh-aw-workflows/`, or fragments in `gh-agent-workflows/gh-aw-fragments/`
2. Run `make compile` (syncs copies, then compiles)
3. Verify 0 errors, 0 warnings
4. Commit all source files, copied files, and generated `.lock.yml` files

```bash
make compile          # sync + compile
```

### Adding a new workflow

1. Create the prompt: `.github/workflows/gh-aw-workflows/<name>-<tier>.md` (e.g., `my-workflow-rwx.md`) — or import a reusable prompt like `gh-aw-workflows/scheduled-report-rwx.md`
2. Add shared fragment imports in the prompt's frontmatter (use `gh-aw-fragments/` prefix)
3. Create the shim: `gh-agent-workflows/<name>.md` with `imports: - gh-aw-workflows/<name>-<tier>.md`
4. Run `make compile` — the sync step copies the shim to `.github/workflows/`, then the compiler generates lock files
5. Verify and commit all files (sources, shim copies, and lock files)
