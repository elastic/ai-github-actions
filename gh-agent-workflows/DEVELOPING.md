# Developing GitHub Agent Workflows

## Architecture

```
gh-agent-workflows/
├── pr-review.md              # Shim: description + trigger + engine + single import
├── pr-review/
│   └── rwx.md                # Agent prompt + tools + network + safe-outputs
├── issue-triage.md
├── issue-triage/
│   └── rwx.md
├── mention-in-issue.md
├── mention-in-issue/
│   └── rwxp.md
├── mention-in-pr.md
├── mention-in-pr/
│   └── rwxp.md
├── docs-drift.md             # Shim: imports scheduled-report/rwx.md + docs-specific instructions
├── scheduled-report/
│   └── rwx.md                # Reusable prompt for scheduled report workflows
│
│   # Internal-only workflows (live in .github/workflows/, not installable via `gh aw add`)
│   .github/workflows/
│   └── gh-aw-upgrade-check.md  # Scheduled check for new gh-aw releases; imports scheduled-report/rwx.md
└── shared/
    ├── elastic-tools.md      # Elastic MCP servers + their network entries
    ├── formatting.md         # Response formatting rules
    ├── rigor.md              # Accuracy & evidence standards
    └── mcp-pagination.md     # MCP token limit guidance
```

**Shims** (`*.md` at the top level) are what consumers install via `gh aw add`. They contain the engine, trigger, permissions, concurrency, roles, description, and a single `imports:` entry. Everything else comes from imports.

**Prompts** (`<workflow>/<tier>.md`) contain the agent instructions, `tools:`, `network:`, and `safe-outputs:`. Each prompt defines the tools it needs and imports the shared fragments. The tier filename indicates the permission level:

- **`rwx.md`** — Read, write (workspace), execute (bash). No push, no PR creation.
- **`rwxp.md`** — Read, write, execute, push. Can create PRs or push to PR branches via safe-outputs.

Adding a new tier (e.g., `r.md` for read-only without bash) is a new sibling file with its own prompt and a new shim that imports it. The gh-aw compiler only supports 2-level import paths (`dir/file.md`), so tiers are files, not subdirectories.

**Shared fragments** (`shared/`) provide cross-workflow configuration and guidance. No `on:` field — validated but never compiled standalone.

## Import Structure

Each shim imports one prompt, which nests the shared fragments:

```
shim (pr-review.md)
 └── pr-review/rwx.md             # agent instructions + tools + network + safe-outputs
      ├── shared/elastic-tools.md  # Elastic MCP servers + network entries
      ├── shared/formatting.md     # response formatting rules
      ├── shared/rigor.md          # accuracy & evidence standards
      └── shared/mcp-pagination.md # pagination best practices
```

**Reusable prompts** can be shared across multiple shims. The shim body (markdown after the frontmatter `---`) is appended to the imported prompt, providing workflow-specific instructions. For example, `scheduled-report/rwx.md` is a generic report agent that multiple shims can import with different report assignments:

```
shim (docs-drift.md)                # schedule + "check for docs drift" instructions
 └── scheduled-report/rwx.md        # generic report framework
      ├── shared/elastic-tools.md
      ├── shared/formatting.md
      ├── shared/rigor.md
      └── shared/mcp-pagination.md

shim (gh-aw-upgrade-check.md)       # schedule + "check for gh-aw upgrades" instructions
 └── scheduled-report/rwx.md        # same generic report framework
      └── ...
```

`gh-aw-upgrade-check` is an **internal-only** workflow — its shim lives directly in `.github/workflows/` (not in `gh-agent-workflows/`) so it is not installable via `gh aw add`. It runs on weekdays to check for new `gh-aw` releases and files issues tagged `[gh-aw-upgrade]`.

To add a new scheduled report, create a shim that imports `scheduled-report/rwx.md` and put the report-specific instructions in the shim body. No new prompt directory needed.

### Shared fragments

| Fragment | Purpose |
| --- | --- |
| [shared/elastic-tools.md](shared/elastic-tools.md) | Elastic MCP servers (`agents-md-generator`, `public-code-search`) and their network entries |
| [shared/formatting.md](shared/formatting.md) | Response formatting rules |
| [shared/rigor.md](shared/rigor.md) | Accuracy & evidence standards |
| [shared/mcp-pagination.md](shared/mcp-pagination.md) | MCP token limit guidance and pagination patterns |
| [shared/safe-output-add-comment.md](shared/safe-output-add-comment.md) | Limitations for `add-comment` (body length, mentions, links) |
| [shared/safe-output-review-comment.md](shared/safe-output-review-comment.md) | Limitations for `create-pull-request-review-comment` (required fields, line rules) |
| [shared/safe-output-submit-review.md](shared/safe-output-submit-review.md) | Limitations for `submit-pull-request-review` (event types, own-PR restriction) |
| [shared/safe-output-push-to-pr.md](shared/safe-output-push-to-pr.md) | Limitations for `push-to-pull-request-branch` (patch size, fork restriction) |
| [shared/safe-output-resolve-thread.md](shared/safe-output-resolve-thread.md) | Limitations for `resolve-pull-request-review-thread` (thread ID format) |
| [shared/safe-output-create-issue.md](shared/safe-output-create-issue.md) | Limitations for `create-issue` (title, labels, assignees) |
| [shared/safe-output-create-pr.md](shared/safe-output-create-pr.md) | Limitations for `create-pull-request` (patch files/size, title) |

### Import rules

- The compiler resolves **all** import paths — including nested ones — relative to `.github/workflows/`, not the importing file. So even imports within `shared/` must use the `shared/` prefix.
- `engine:`, `on:`, `concurrency:`, `timeout-minutes:`, `strict:`, `roles:` are **not importable** — they must be in the shim.
- `safe-outputs:` in the main workflow override imported defaults. `tools:` merge additively.

## Local Development

### How compilation works

The `gh-aw` compiler processes `.md` files in `.github/workflows/`. Since our source-of-truth files live in `gh-agent-workflows/` (outside `.github/`), we bridge the gap with symlinks — both shim files and import directories in `.github/workflows/` point back to `gh-agent-workflows/`:

```
.github/workflows/
├── shared -> ../../gh-agent-workflows/shared
├── pr-review -> ../../gh-agent-workflows/pr-review
├── pr-review.md -> ../../gh-agent-workflows/pr-review.md
├── pr-review.lock.yml    # compiled output
├── scheduled-report -> ../../gh-agent-workflows/scheduled-report
├── docs-drift.md -> ../../gh-agent-workflows/docs-drift.md
├── docs-drift.lock.yml   # compiled output
├── gh-aw-upgrade-check.md   # repo-specific (not symlinked)
├── gh-aw-upgrade-check.lock.yml
└── ...
```

> **Note:** This repo has `core.symlinks=false`, so git checks out symlinks as text files containing the target path. `make sync` (run automatically by `make compile`) detects these and converts them to real filesystem symlinks before compilation.

Consumers never need symlinks — `gh aw add` rewrites imports to remote references.

### Editing workflows

1. Edit source files in `gh-agent-workflows/` (shims, prompts, or shared fragments)
2. Run `make compile` (compiles, auto-fixes symlinks if needed)
3. Verify 0 errors, 0 warnings
4. Commit both the source files and the generated `.lock.yml` files

```bash
make compile          # ensure symlinks + compile
```

### Adding a new workflow

1. Create the shim: `gh-agent-workflows/<name>.md`
2. Create the prompt: `gh-agent-workflows/<name>/<tier>.md` (e.g., `rwx.md` or `rwxp.md`) — or import a reusable prompt like `scheduled-report/rwx.md`
3. Add shared fragment imports in the prompt's frontmatter
4. Create symlinks in `.github/workflows/`:

```bash
cd .github/workflows
ln -s ../../gh-agent-workflows/<name>.md <name>.md     # shim
ln -s ../../gh-agent-workflows/<name> <name>           # import directory (skip if using a reusable prompt)
```

5. Register the symlinks in git as mode `120000`:

```bash
git update-index --add --cacheinfo 120000,$(echo -n "../../gh-agent-workflows/<name>.md" | git hash-object -w --stdin),.github/workflows/<name>.md
git update-index --add --cacheinfo 120000,$(echo -n "../../gh-agent-workflows/<name>" | git hash-object -w --stdin),.github/workflows/<name>
```

6. Run `make compile` and verify

### Recreating symlinks

`make sync` automatically converts text-file symlinks (created by git with `core.symlinks=false`) to real filesystem symlinks. Just run `make compile` after a fresh clone.
