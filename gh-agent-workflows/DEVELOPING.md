# Developing GitHub Agent Workflows

## Architecture

```text
gh-agent-workflows/
├── pr-review.yml              # Trigger: event triggers + uses: .lock.yml (example + dogfood)
├── issue-triage.yml
├── mention-in-issue.yml
├── docs-drift.yml
├── ...
└── README.md, DEVELOPING.md   # Consumer-facing docs

.github/workflows/
├── gh-aw-fragments/            # Shared fragments (real directory)
│   ├── elastic-tools.md
│   ├── formatting.md
│   ├── rigor.md
│   ├── mcp-pagination.md
│   ├── scheduled-report.md     # Shared scheduled report prompt
│   └── safe-output-*.md
├── gh-aw-pr-review.md          # Workflow: self-contained (prompt + config)
├── gh-aw-pr-review.lock.yml    # Compiled output
├── trigger-pr-review.yml       # Copied from gh-agent-workflows/ (event triggers)
├── ...
└── gh-aw-upgrade-check.md      # Internal-only scheduled check
```

**Workflows** (`.github/workflows/gh-aw-*.md`) are self-contained agent workflow definitions. Each file contains the engine, `workflow_call` trigger (with standard inputs), permissions, concurrency, roles, description, tools, network, safe-outputs, and the full agent prompt. Workflows import only shared fragments from `gh-aw-fragments/`. They trigger **only** on `workflow_call` — they do not have schedule, event, or dispatch triggers directly.

**Triggers** (`gh-agent-workflows/*.yml`) are plain YAML files that define the actual event triggers (schedule, PR events, slash commands, etc.) and call the compiled `.lock.yml` via `uses:`. When copied to `.github/workflows/` by `scripts/dogfood.sh`, they become `trigger-*.yml` (e.g., `pr-review.yml` → `trigger-pr-review.yml`). They serve two purposes: (1) dogfood for running workflows in this repo, and (2) examples for consumer repos to copy and adapt. Triggers are NOT compiled by `gh-aw` — they are plain GitHub Actions YAML.

**Shared fragments** (`.github/workflows/gh-aw-fragments/`) provide cross-workflow configuration and guidance. Fragments live directly in this directory — no symlinks. No `on:` field — validated but never compiled standalone. For example, `scheduled-report.md` provides a shared framework for scheduled report workflows.

## Import Structure

Each workflow imports fragments directly and contains its own full prompt:

```text
workflow (gh-aw-pr-review.md)
 ├── gh-aw-fragments/elastic-tools.md
 ├── gh-aw-fragments/formatting.md
 ├── gh-aw-fragments/rigor.md
 ├── gh-aw-fragments/mcp-pagination.md
 └── gh-aw-fragments/review-process.md
```

For scheduled reports:

```text
workflow (gh-aw-docs-drift.md)
 ├── gh-aw-fragments/scheduled-report.md   # shared report framework
 ├── gh-aw-fragments/elastic-tools.md
 ├── gh-aw-fragments/formatting.md
 └── ...
```

`gh-aw-upgrade-check` is an **internal-only** workflow — its shim lives directly in `.github/workflows/` (not in `gh-agent-workflows/`) so it is not installable via `gh aw add`. It runs on weekdays to check for new `gh-aw` releases and files issues tagged `[gh-aw-upgrade]`.

### Shared fragments

Fragments live in `.github/workflows/gh-aw-fragments/`. Workflows import them using the `gh-aw-fragments/` prefix.

| Fragment | Purpose |
| --- | --- |
| [gh-aw-fragments/elastic-tools.md](../.github/workflows/gh-aw-fragments/elastic-tools.md) | Elastic MCP servers (`agents-md-generator`, `public-code-search`) and their network entries |
| [gh-aw-fragments/formatting.md](../.github/workflows/gh-aw-fragments/formatting.md) | Response formatting rules |
| [gh-aw-fragments/rigor.md](../.github/workflows/gh-aw-fragments/rigor.md) | Accuracy & evidence standards |
| [gh-aw-fragments/mcp-pagination.md](../.github/workflows/gh-aw-fragments/mcp-pagination.md) | MCP token limit guidance and pagination patterns |
| [gh-aw-fragments/scheduled-report.md](../.github/workflows/gh-aw-fragments/scheduled-report.md) | Shared scheduled report framework |
| [gh-aw-fragments/review-process.md](../.github/workflows/gh-aw-fragments/review-process.md) | Shared code review process, comment format, severity classification, and review criteria |
| [gh-aw-fragments/messages-footer.md](../.github/workflows/gh-aw-fragments/messages-footer.md) | Global message footer appended to all comments and reviews |
| [gh-aw-fragments/safe-output-add-comment.md](../.github/workflows/gh-aw-fragments/safe-output-add-comment.md) | Limitations for `add-comment` (body length, mentions, links) |
| [gh-aw-fragments/safe-output-review-comment.md](../.github/workflows/gh-aw-fragments/safe-output-review-comment.md) | Limitations for `create-pull-request-review-comment` (required fields, line rules) |
| [gh-aw-fragments/safe-output-submit-review.md](../.github/workflows/gh-aw-fragments/safe-output-submit-review.md) | Limitations for `submit-pull-request-review` (event types, own-PR restriction) |
| [gh-aw-fragments/safe-output-push-to-pr.md](../.github/workflows/gh-aw-fragments/safe-output-push-to-pr.md) | Limitations for `push-to-pull-request-branch` (patch size, fork restriction) |
| [gh-aw-fragments/safe-output-resolve-thread.md](../.github/workflows/gh-aw-fragments/safe-output-resolve-thread.md) | Limitations for `resolve-pull-request-review-thread` (thread ID format) |
| [gh-aw-fragments/safe-output-create-issue.md](../.github/workflows/gh-aw-fragments/safe-output-create-issue.md) | Limitations for `create-issue` (title, labels, assignees) |
| [gh-aw-fragments/safe-output-create-pr.md](../.github/workflows/gh-aw-fragments/safe-output-create-pr.md) | Limitations for `create-pull-request` (patch files/size, title) |

### Import rules

- The compiler only supports **2-level** import paths (`dir/file.md`). Paths with 3+ segments are interpreted as remote GitHub references.
- Workflow `.md` files live directly in `.github/workflows/`. For **remote consumers**, `gh aw add` rewrites imports to remote references.
- `engine:`, `on:`, `concurrency:`, `timeout-minutes:`, `strict:`, `roles:` are **not importable** — they must be in the workflow `.md`.
- `safe-outputs:` in the main workflow override imported defaults. `tools:` merge additively.

## Local Development

### How compilation works

The `gh-aw` compiler processes `.md` files in `.github/workflows/`. `make sync` (which runs `scripts/dogfood.sh`) copies `*.yml` files from `gh-agent-workflows/` to `.github/workflows/trigger-*.yml`. Workflow `.md` files and `gh-aw-fragments/` live directly in `.github/workflows/` — no symlinks. `gh-aw-fragments/` is a real directory.

```text
.github/workflows/
├── gh-aw-fragments/            # Shared fragments (real directory)
│   ├── elastic-tools.md
│   ├── scheduled-report.md
│   └── ...
├── gh-aw-pr-review.md          # Workflow (self-contained)
├── gh-aw-pr-review.lock.yml    # compiled output
├── trigger-pr-review.yml       # copied from gh-agent-workflows/ (event triggers)
├── gh-aw-docs-drift.md
├── gh-aw-docs-drift.lock.yml
├── trigger-docs-drift.yml
├── gh-aw-upgrade-check.md      # repo-specific internal workflow
├── gh-aw-upgrade-check.lock.yml
└── ...
```

Trigger `.yml` files are copied from `gh-agent-workflows/` as-is by `scripts/dogfood.sh` (with `trigger-` prefix added).

### Editing workflows

1. Edit workflows in `.github/workflows/gh-aw-*.md`, triggers in `gh-agent-workflows/*.yml`, or fragments in `.github/workflows/gh-aw-fragments/`
2. Run `make compile` (syncs triggers, then compiles)
3. Verify 0 errors, 0 warnings
4. Commit all source files, trigger files, and generated `.lock.yml` files

```bash
make compile          # sync + compile
```

### Adding a new workflow

1. Create the workflow `.github/workflows/gh-aw-<name>.md` with imports (fragments), tools, network, safe-outputs, and the full prompt
2. Create the trigger `gh-agent-workflows/<name>.yml` with event triggers and `uses: ./.github/workflows/gh-aw-<name>.lock.yml`
3. Run `make compile`
4. Verify and commit

### workflow_call Convention

All shims include a `workflow_call` trigger with two standard inputs and one secret:

```yaml
on:
  workflow_call:
    inputs:
      additional-instructions:
        description: "Repo-specific instructions appended to the agent prompt"
        type: string
        required: false
        default: ""
      setup-commands:
        description: "Shell commands to run before the agent starts (dependency install, build, etc.)"
        type: string
        required: false
        default: ""
    secrets:
      COPILOT_GITHUB_TOKEN:
        required: true
```

And a setup step that runs the caller's commands:

```yaml
steps:
  - name: Repo-specific setup
    if: ${{ inputs.setup-commands != '' }}
    env:
      SETUP_COMMANDS: ${{ inputs.setup-commands }}
    run: eval "$SETUP_COMMANDS"
```

The `setup-commands` input uses environment variable indirection (`env:` + `eval`) to satisfy the compiler's template injection checks. This is safe because `workflow_call` inputs are set by the calling workflow's YAML, not by external users.

Consumer repos call the compiled `.lock.yml` via `uses:` in a plain YAML workflow. See [README.md](README.md) for caller templates.

### Trigger files

Each workflow has a corresponding `<name>.yml` in `gh-agent-workflows/` that defines the actual event triggers and calls the compiled `.lock.yml`. These are plain YAML (not compiled by gh-aw) and are copied to `.github/workflows/trigger-<name>.yml` by `scripts/dogfood.sh` for dogfooding.

Consumer repos use these as starting points: copy the trigger file from `gh-agent-workflows/`, change the `uses:` path from `./.github/workflows/gh-aw-<name>.lock.yml` to `elastic/ai-github-actions/.github/workflows/gh-aw-<name>.lock.yml@main`, and customize the `with:` inputs.
