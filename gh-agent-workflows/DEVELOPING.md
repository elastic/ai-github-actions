# Developing GitHub Agent Workflows

## Architecture

```text
gh-agent-workflows/
├── pr-review/
│   ├── README.md              # Per-workflow docs (trigger, inputs, safe outputs)
│   ├── example.yml            # Trigger: event triggers + uses: .lock.yml (example + dogfood)
│   └── dogfood-with.yml       # Optional: with: overrides applied when dogfooding
├── issue-triage/
│   ├── README.md
│   └── example.yml
├── mention-in-issue/
│   ├── README.md
│   └── example.yml
├── ...
└── README.md, DEVELOPING.md   # Consumer-facing docs

.github/workflows/
├── gh-aw-fragments/            # Shared fragments (real directory)
│   ├── elastic-tools.md
│   ├── formatting.md
│   ├── rigor.md
│   ├── mcp-pagination.md
│   ├── scheduled-audit.md     # Shared audit framework (detect and report)
│   ├── scheduled-fix.md       # Shared fix framework (pick up issue and PR)
│   └── safe-output-*.md
├── gh-aw-pr-review.md          # Workflow: self-contained (prompt + config)
├── gh-aw-pr-review.lock.yml    # Compiled output
├── trigger-pr-review.yml       # Copied from gh-agent-workflows/pr-review/example.yml
├── ...
└── upgrade-check.md            # Internal-only scheduled check (no gh-aw- prefix)
```

**Workflows** (`.github/workflows/gh-aw-*.md`) are self-contained agent workflow definitions. Each file contains the engine, `workflow_call` trigger (with standard inputs), permissions, concurrency, roles, description, tools, network, safe-outputs, and the full agent prompt. Workflows import only shared fragments from `gh-aw-fragments/`. They trigger **only** on `workflow_call` — they do not have schedule, event, or dispatch triggers directly.

**Triggers** (`gh-agent-workflows/<name>/example.yml`) are plain YAML files that define the actual event triggers (schedule, PR events, slash commands, etc.) and call the compiled `.lock.yml` via `uses:`. When copied to `.github/workflows/` by `scripts/dogfood.sh`, they become `trigger-<name>.yml` (e.g., `pr-review/example.yml` → `trigger-pr-review.yml`) for workflows not listed in `EXCLUDED_WORKFLOWS`. They serve two purposes: (1) dogfood for running workflows in this repo, and (2) examples for consumer repos to copy and adapt. Triggers are NOT compiled by `gh-aw` — they are plain GitHub Actions YAML.

**Dogfood overrides** (`gh-agent-workflows/<name>/dogfood-with.yml`) are optional files containing `with:` input values that the dogfood script injects into the generated trigger. This lets us run workflows at different settings in this repo (e.g., `intensity: aggressive`) while keeping the examples at conservative defaults for consumers. If no `dogfood-with.yml` exists, the trigger is copied as-is from the example.

Each workflow directory also contains a `README.md` with trigger details, inputs, and safe outputs.

**Shared fragments** (`.github/workflows/gh-aw-fragments/`) provide cross-workflow configuration and guidance. Fragments live directly in this directory — no symlinks. No `on:` field — validated but never compiled standalone. For example, `scheduled-audit.md` provides a shared framework for scheduled audit workflows.

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

For scheduled audits (detectors):

```text
workflow (gh-aw-docs-patrol.md)
 ├── gh-aw-fragments/scheduled-audit.md   # shared audit framework
 ├── gh-aw-fragments/elastic-tools.md
 ├── gh-aw-fragments/formatting.md
 └── ...
```

For scheduled fixes (fixers):

```text
workflow (gh-aw-text-beautifier.md)
 ├── gh-aw-fragments/scheduled-fix.md     # shared fix framework
 ├── gh-aw-fragments/workflow-edit-guardrails.md
 ├── gh-aw-fragments/safe-output-create-pr.md
 ├── gh-aw-fragments/elastic-tools.md
 └── ...
```

`upgrade-check` is an **internal-only** workflow — it lives directly in `.github/workflows/` without the `gh-aw-` prefix (not in `gh-agent-workflows/`) so it is not installable via `gh aw add`. Internal-only workflows (`upgrade-check`, `workflow-patrol`, `downstream-users`) omit the `gh-aw-` prefix to distinguish them from published workflows.

### Shared fragments

Fragments live in `.github/workflows/gh-aw-fragments/`. Workflows import them using the `gh-aw-fragments/` prefix.

| Fragment | Purpose |
| --- | --- |
| [gh-aw-fragments/elastic-tools.md](../.github/workflows/gh-aw-fragments/elastic-tools.md) | Elastic MCP servers (`agents-md-generator`, `public-code-search`) and their network entries |
| [gh-aw-fragments/formatting.md](../.github/workflows/gh-aw-fragments/formatting.md) | Response formatting rules |
| [gh-aw-fragments/rigor.md](../.github/workflows/gh-aw-fragments/rigor.md) | Accuracy & evidence standards |
| [gh-aw-fragments/mcp-pagination.md](../.github/workflows/gh-aw-fragments/mcp-pagination.md) | MCP token limit guidance and pagination patterns |
| [gh-aw-fragments/scheduled-audit.md](../.github/workflows/gh-aw-fragments/scheduled-audit.md) | Shared scheduled audit framework (detect and report) |
| [gh-aw-fragments/scheduled-fix.md](../.github/workflows/gh-aw-fragments/scheduled-fix.md) | Shared scheduled fix framework (pick up issue and create PR) |
| [gh-aw-fragments/review-process.md](../.github/workflows/gh-aw-fragments/review-process.md) | Shared code review process, comment format, severity classification, and review criteria |
| [gh-aw-fragments/messages-footer.md](../.github/workflows/gh-aw-fragments/messages-footer.md) | Wires the `messages-footer` input to `safe-outputs.messages.footer`; consumers override the footer via the workflow input |
| [gh-aw-fragments/safe-output-add-comment.md](../.github/workflows/gh-aw-fragments/safe-output-add-comment.md) | Limitations for `add-comment` (body length, mentions, links) |
| [gh-aw-fragments/safe-output-review-comment.md](../.github/workflows/gh-aw-fragments/safe-output-review-comment.md) | Limitations for `create-pull-request-review-comment` (required fields, line rules) |
| [gh-aw-fragments/safe-output-submit-review.md](../.github/workflows/gh-aw-fragments/safe-output-submit-review.md) | Limitations for `submit-pull-request-review` (event types, own-PR restriction) |
| [gh-aw-fragments/safe-output-push-to-pr.md](../.github/workflows/gh-aw-fragments/safe-output-push-to-pr.md) | Limitations for `push-to-pull-request-branch` (patch size, fork restriction) |
| [gh-aw-fragments/safe-output-resolve-thread.md](../.github/workflows/gh-aw-fragments/safe-output-resolve-thread.md) | Limitations for `resolve-pull-request-review-thread` (thread ID format) |
| [gh-aw-fragments/safe-output-create-issue.md](../.github/workflows/gh-aw-fragments/safe-output-create-issue.md) | Limitations for `create-issue` (title, labels, assignees) |
| [gh-aw-fragments/safe-output-create-pr.md](../.github/workflows/gh-aw-fragments/safe-output-create-pr.md) | Limitations for `create-pull-request` (patch files/size, title) |
| [gh-aw-fragments/previous-findings.md](../.github/workflows/gh-aw-fragments/previous-findings.md) | Fetches previous issues filed by this agent (using `inputs.title-prefix`) and instructs the agent not to repeat them |

### Import rules

- The compiler only supports **2-level** import paths (`dir/file.md`). Paths with 3+ segments are interpreted as remote GitHub references.
- Workflow `.md` files live directly in `.github/workflows/`. For **remote consumers**, `gh aw add` rewrites imports to remote references.
- `engine:`, `on:`, `concurrency:`, `timeout-minutes:`, `strict:`, `roles:` are **not importable** — they must be in the workflow `.md`.
- `safe-outputs:` in the main workflow override imported defaults. `tools:` merge additively.

## Local Development

### How compilation works

The `gh-aw` compiler processes `.md` files in `.github/workflows/`. `make sync` (which runs `scripts/dogfood.sh`) copies `example.yml` files from `gh-agent-workflows/*/` to `.github/workflows/trigger-*.yml` for workflows not listed in `EXCLUDED_WORKFLOWS`, injecting any `dogfood-with.yml` overrides. Workflow `.md` files and `gh-aw-fragments/` live directly in `.github/workflows/` — no symlinks. `gh-aw-fragments/` is a real directory.

```text
.github/workflows/
├── gh-aw-fragments/            # Shared fragments (real directory)
│   ├── elastic-tools.md
│   ├── scheduled-audit.md
│   ├── scheduled-fix.md
│   └── ...
├── gh-aw-pr-review.md          # Workflow (self-contained)
├── gh-aw-pr-review.lock.yml    # compiled output
├── trigger-pr-review.yml       # copied from gh-agent-workflows/pr-review/example.yml
├── gh-aw-docs-patrol.md
├── gh-aw-docs-patrol.lock.yml
├── trigger-docs-patrol.yml
├── gh-aw-newbie-contributor-patrol.md
├── gh-aw-newbie-contributor-patrol.lock.yml
├── trigger-newbie-contributor-patrol.yml
├── upgrade-check.md            # internal-only (no gh-aw- prefix)
├── upgrade-check.lock.yml
└── ...
```

Trigger `example.yml` files are copied from `gh-agent-workflows/*/` by `scripts/dogfood.sh` (with `trigger-` prefix added) for workflows not listed in `EXCLUDED_WORKFLOWS`. If a `dogfood-with.yml` exists alongside the example, its contents replace any existing `with:` block in the generated trigger.

### Editing workflows

1. Edit workflows in `.github/workflows/gh-aw-*.md`, triggers in `gh-agent-workflows/*/example.yml`, or fragments in `.github/workflows/gh-aw-fragments/`
2. Run `make compile` (syncs triggers, then compiles)
3. Verify 0 errors, 0 warnings
4. Commit source files (`gh-aw-*.md`, `example.yml`, fragments) and the generated `.lock.yml` and `trigger-*.yml` files

> **Do not edit `.lock.yml` files directly.** They are compiled output generated by `make compile` from the corresponding `.md` workflow source. Any manual edits will be overwritten on the next compile.

```bash
make compile          # sync + compile
```

### Adding a new workflow

1. Create the workflow `.github/workflows/gh-aw-<name>.md` with imports (fragments), tools, network, safe-outputs, and the full prompt
2. Create `gh-agent-workflows/<name>/example.yml` with event triggers and `uses: elastic/ai-github-actions/.github/workflows/gh-aw-<name>.lock.yml@v0`
3. Create `gh-agent-workflows/<name>/README.md` with trigger details, inputs, and safe outputs
4. Run `make compile`
5. Verify and commit

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

Each non-internal workflow has a corresponding `example.yml` in `gh-agent-workflows/<name>/` that defines the actual event triggers and calls the compiled `.lock.yml`. These are plain YAML (not compiled by gh-aw) and are copied to `.github/workflows/trigger-<name>.yml` by `scripts/dogfood.sh` for dogfooding when the workflow is not listed in `EXCLUDED_WORKFLOWS` (see `scripts/dogfood.sh` for the current list).

> **Do not edit `trigger-*.yml` files directly.** They are auto-generated by `scripts/dogfood.sh` (run via `make compile`) and any manual changes will be overwritten. To change a trigger, edit `gh-agent-workflows/<name>/example.yml` (or `dogfood-with.yml` for dogfood-only overrides) and run `make compile`.

Consumer repos copy a workflow's `example.yml` into their `.github/workflows/` directory and customize the `with:` inputs. The `uses:` path already points to the remote compiled workflow.

### Dogfood overrides

To run a workflow at different settings in this repo without changing the consumer-facing example, create a `dogfood-with.yml` alongside the `example.yml`:

```yaml
# gh-agent-workflows/pr-review/dogfood-with.yml
intensity: aggressive
minimum_severity: nitpick
```

The dogfood script injects these as a `with:` block in the generated trigger, replacing any existing `with:` block (including commented-out defaults). The file contains only the key-value pairs — no `with:` key, no indentation.
