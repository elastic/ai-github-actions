# Developing GitHub Agent Workflows

## Architecture

```
gh-agent-workflows/
├── pr-review.md              # Shim: description + trigger + engine + single import
├── issue-triage.md
├── mention-in-issue.md
├── mention-in-pr.md
├── docs-drift.md             # Shim: imports scheduled-report-rwx.md + docs-specific instructions
└── gh-aw-workflows -> ../.github/workflows/gh-aw-workflows  # symlink for local compilation

.github/workflows/
├── gh-aw-fragments/          # Shared fragments (real files)
│   ├── elastic-tools.md      # Elastic MCP servers + their network entries
│   ├── formatting.md         # Response formatting rules
│   ├── rigor.md              # Accuracy & evidence standards
│   ├── mcp-pagination.md     # MCP token limit guidance
│   └── safe-output-*.md      # Safe-output declarations + agent guidance
├── gh-aw-workflows/          # Prompts (real files)
│   ├── pr-review-rwx.md      # PR review agent prompt
│   ├── issue-triage-rwx.md   # Issue triage agent prompt
│   ├── mention-in-pr-rwxp.md # Mention-in-PR agent prompt (with push)
│   ├── mention-in-issue-rwxp.md  # Mention-in-issue agent prompt (with push)
│   └── scheduled-report-rwx.md   # Reusable scheduled report prompt
└── gh-aw-upgrade-check.md    # Internal-only scheduled check for gh-aw releases
```

**Shims** (`*.md` at the top level) are what consumers install via `gh aw add`. They contain the engine, trigger, permissions, concurrency, roles, description, and a single `imports:` entry. Everything else comes from imports.

**Prompts** (`.github/workflows/gh-aw-workflows/`) contain the agent instructions, `tools:`, `network:`, and `safe-outputs:`. Each prompt imports the shared fragments it needs. Filenames follow the pattern `<workflow>-<tier>.md` where the tier indicates the permission level:

- **`rwx`** — Read, write (workspace), execute (bash). No push, no PR creation.
- **`rwxp`** — Read, write, execute, push. Can create PRs or push to PR branches via safe-outputs.

The gh-aw compiler only supports 2-level import paths (`dir/file.md`), so prompts are flattened files (e.g., `gh-aw-workflows/pr-review-rwx.md`), not nested subdirectories. Adding a new tier is a new file with its own prompt and a new shim that imports it.

**Shared fragments** (`.github/workflows/gh-aw-fragments/`) provide cross-workflow configuration and guidance. These are real files (not symlinks) that live directly in the workflows directory where the compiler expects them. No `on:` field — validated but never compiled standalone.

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

Fragments live in `.github/workflows/gh-aw-fragments/` as real files (not symlinks). Prompts import them using the `gh-aw-fragments/` prefix.

| Fragment | Purpose |
| --- | --- |
| [gh-aw-fragments/elastic-tools.md](../.github/workflows/gh-aw-fragments/elastic-tools.md) | Elastic MCP servers (`agents-md-generator`, `public-code-search`) and their network entries |
| [gh-aw-fragments/formatting.md](../.github/workflows/gh-aw-fragments/formatting.md) | Response formatting rules |
| [gh-aw-fragments/rigor.md](../.github/workflows/gh-aw-fragments/rigor.md) | Accuracy & evidence standards |
| [gh-aw-fragments/mcp-pagination.md](../.github/workflows/gh-aw-fragments/mcp-pagination.md) | MCP token limit guidance and pagination patterns |
| [gh-aw-fragments/safe-output-add-comment.md](../.github/workflows/gh-aw-fragments/safe-output-add-comment.md) | Limitations for `add-comment` (body length, mentions, links) |
| [gh-aw-fragments/safe-output-review-comment.md](../.github/workflows/gh-aw-fragments/safe-output-review-comment.md) | Limitations for `create-pull-request-review-comment` (required fields, line rules) |
| [gh-aw-fragments/safe-output-submit-review.md](../.github/workflows/gh-aw-fragments/safe-output-submit-review.md) | Limitations for `submit-pull-request-review` (event types, own-PR restriction) |
| [gh-aw-fragments/safe-output-push-to-pr.md](../.github/workflows/gh-aw-fragments/safe-output-push-to-pr.md) | Limitations for `push-to-pull-request-branch` (patch size, fork restriction) |
| [gh-aw-fragments/safe-output-resolve-thread.md](../.github/workflows/gh-aw-fragments/safe-output-resolve-thread.md) | Limitations for `resolve-pull-request-review-thread` (thread ID format) |
| [gh-aw-fragments/safe-output-create-issue.md](../.github/workflows/gh-aw-fragments/safe-output-create-issue.md) | Limitations for `create-issue` (title, labels, assignees) |
| [gh-aw-fragments/safe-output-create-pr.md](../.github/workflows/gh-aw-fragments/safe-output-create-pr.md) | Limitations for `create-pull-request` (patch files/size, title) |

### Import rules

- The compiler only supports **2-level** import paths (`dir/file.md`). Paths with 3+ segments are interpreted as remote GitHub references. This is why prompts are flattened (e.g., `gh-aw-workflows/pr-review-rwx.md`, not `gh-aw-workflows/pr-review/rwx.md`).
- For **local compilation**, shim symlinks resolve imports relative to their target location (`gh-agent-workflows/`). A symlink at `gh-agent-workflows/gh-aw-workflows` points back to `.github/workflows/gh-aw-workflows/` so the compiler can find prompts locally. For **remote consumers**, `gh aw add` rewrites imports to remote references relative to `.github/workflows/`.
- `engine:`, `on:`, `concurrency:`, `timeout-minutes:`, `strict:`, `roles:` are **not importable** — they must be in the shim.
- `safe-outputs:` in the main workflow override imported defaults. `tools:` merge additively.

## Local Development

### How compilation works

The `gh-aw` compiler processes `.md` files in `.github/workflows/`. Shims live in `gh-agent-workflows/` and are symlinked into `.github/workflows/`. Prompts and fragments are **real files** in `.github/workflows/` — no symlinks needed for them:

```
.github/workflows/
├── gh-aw-fragments/              # real files — shared fragments
│   ├── elastic-tools.md
│   ├── formatting.md
│   └── ...
├── gh-aw-workflows/              # real files — prompts
│   ├── pr-review-rwx.md
│   ├── scheduled-report-rwx.md
│   └── ...
├── pr-review.md -> ../../gh-agent-workflows/pr-review.md   # shim symlink
├── pr-review.lock.yml            # compiled output
├── docs-drift.md -> ../../gh-agent-workflows/docs-drift.md
├── docs-drift.lock.yml
├── gh-aw-upgrade-check.md        # repo-specific (not symlinked)
├── gh-aw-upgrade-check.lock.yml
└── ...
```

A reverse symlink at `gh-agent-workflows/gh-aw-workflows → ../.github/workflows/gh-aw-workflows` lets the compiler resolve imports when following shim symlinks during local compilation.

> **Note:** This repo has `core.symlinks=false`, so git checks out symlinks as text files containing the target path. `make sync` (run automatically by `make compile`) detects these and converts them to real filesystem symlinks before compilation.

Consumers never need symlinks — `gh aw add` rewrites imports to remote references.

### Editing workflows

1. Edit shims in `gh-agent-workflows/`, prompts in `.github/workflows/gh-aw-workflows/`, or fragments in `.github/workflows/gh-aw-fragments/`
2. Run `make compile` (compiles, auto-fixes symlinks if needed)
3. Verify 0 errors, 0 warnings
4. Commit both the source files and the generated `.lock.yml` files

```bash
make compile          # ensure symlinks + compile
```

### Adding a new workflow

1. Create the prompt: `.github/workflows/gh-aw-workflows/<name>-<tier>.md` (e.g., `my-workflow-rwx.md`) — or import a reusable prompt like `gh-aw-workflows/scheduled-report-rwx.md`
2. Add shared fragment imports in the prompt's frontmatter (use `gh-aw-fragments/` prefix)
3. Create the shim: `gh-agent-workflows/<name>.md` with `imports: - gh-aw-workflows/<name>-<tier>.md`
4. Create a shim symlink in `.github/workflows/`:

```bash
cd .github/workflows
ln -s ../../gh-agent-workflows/<name>.md <name>.md
```

5. Register the symlink in git as mode `120000`:

```bash
git update-index --add --cacheinfo 120000,$(echo -n "../../gh-agent-workflows/<name>.md" | git hash-object -w --stdin),.github/workflows/<name>.md
```

6. Run `make compile` and verify

### Recreating symlinks

`make sync` automatically converts text-file symlinks (created by git with `core.symlinks=false`) to real filesystem symlinks. Just run `make compile` after a fresh clone.
