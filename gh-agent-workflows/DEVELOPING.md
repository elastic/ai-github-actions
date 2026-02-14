# Developing GitHub Agent Workflows

## Architecture

```
gh-agent-workflows/
├── pr-review.md              # Shim: trigger + engine + single import
├── pr-review/
│   └── prompt.md             # Agent prompt + safe-outputs
├── issue-triage.md
├── issue-triage/
│   └── prompt.md
├── mention-in-issue.md
├── mention-in-issue/
│   └── prompt.md
├── mention-in-pr.md
├── mention-in-pr/
│   └── prompt.md
└── shared/
    ├── elastic-tools.md      # Tools, MCP servers, network config
    ├── formatting.md         # Response formatting rules
    ├── rigor.md              # Accuracy & evidence standards
    └── mcp-pagination.md     # MCP token limit guidance
```

**Shims** (`*.md` at the top level) are what consumers install via `gh aw add`. They contain only the engine, trigger, permissions, concurrency, roles, and a single `imports:` entry. Everything else comes from imports.

**Prompts** (`*/prompt.md`) contain the agent instructions and `safe-outputs:`. Each prompt imports the shared fragments.

**Shared fragments** (`shared/`) provide cross-workflow configuration and guidance. No `on:` field — validated but never compiled standalone.

## Import Structure

Each shim imports one prompt, which nests the shared fragments:

```
shim (pr-review.md)
 └── pr-review/prompt.md          # agent instructions + safe-outputs
      ├── shared/elastic-tools.md  # tools, MCP servers, network
      ├── shared/formatting.md     # response formatting rules
      ├── shared/rigor.md          # accuracy & evidence standards
      └── shared/mcp-pagination.md # pagination best practices
```

### Shared fragments

| Fragment | Purpose |
| --- | --- |
| [shared/elastic-tools.md](shared/elastic-tools.md) | GitHub MCP toolsets, MCP servers (`agents-md-generator`, `public-code-search`), network allow-list |
| [shared/formatting.md](shared/formatting.md) | Response formatting rules |
| [shared/rigor.md](shared/rigor.md) | Accuracy & evidence standards |
| [shared/mcp-pagination.md](shared/mcp-pagination.md) | MCP token limit guidance and pagination patterns |

### Import rules

- The compiler resolves **all** import paths — including nested ones — relative to `.github/workflows/`, not the importing file. So even imports within `shared/` must use the `shared/` prefix.
- `engine:`, `on:`, `concurrency:`, `timeout-minutes:`, `strict:`, `roles:` are **not importable** — they must be in the shim.
- `safe-outputs:` in the main workflow override imported defaults. `tools:` merge additively.

## Local Development

### How compilation works

The `gh-aw` compiler processes `.md` files in `.github/workflows/`. Since our source-of-truth files live in `gh-agent-workflows/` (outside `.github/`), we bridge the gap with:

1. **`make sync`** — copies shim files from `gh-agent-workflows/*.md` to `.github/workflows/*.md`
2. **Symlinks** — point `.github/workflows/` subdirectories back to `gh-agent-workflows/` for import resolution:

```
.github/workflows/
├── shared -> ../../gh-agent-workflows/shared
├── pr-review -> ../../gh-agent-workflows/pr-review
├── issue-triage -> ../../gh-agent-workflows/issue-triage
├── mention-in-issue -> ../../gh-agent-workflows/mention-in-issue
├── mention-in-pr -> ../../gh-agent-workflows/mention-in-pr
├── pr-review.md          # synced from gh-agent-workflows/
├── pr-review.lock.yml    # compiled output
└── ...
```

Consumers never need symlinks — `gh aw add` rewrites imports to remote references.

### Editing workflows

1. Edit source files in `gh-agent-workflows/` (shims, prompts, or shared fragments)
2. Run `make compile` (syncs + compiles)
3. Verify 0 errors, 0 warnings
4. Commit both the source files and the generated `.lock.yml` files

```bash
make compile          # sync + compile
make sync             # sync only
```

### Adding a new workflow

1. Create the shim: `gh-agent-workflows/<name>.md`
2. Create the prompt: `gh-agent-workflows/<name>/prompt.md`
3. Add shared fragment imports in the prompt's frontmatter
4. Create a symlink: `ln -s ../../gh-agent-workflows/<name> .github/workflows/<name>`
5. Run `make compile` and verify

### Recreating symlinks

If symlinks are missing (e.g., fresh clone):

```bash
cd .github/workflows
ln -s ../../gh-agent-workflows/shared shared
ln -s ../../gh-agent-workflows/pr-review pr-review
ln -s ../../gh-agent-workflows/issue-triage issue-triage
ln -s ../../gh-agent-workflows/mention-in-issue mention-in-issue
ln -s ../../gh-agent-workflows/mention-in-pr mention-in-pr
```
