# gh-aw Safe Outputs: Validation Rules and Limitations

**Source:** Examined source code from [github/gh-aw](https://github.com/github/gh-aw) repository (main branch)

**Files analyzed:**
- `add_labels.cjs`, `add_reaction.cjs`, `assign_issue.cjs`, `close_issue.cjs`, `close_pull_request.cjs`, `link_sub_issue.cjs`
- Supporting modules: `safe_output_validator.cjs`, `limit_enforcement_helpers.cjs`, `sanitize_content.cjs`, `sanitize_content_core.cjs`, `sanitize_label_content.cjs`, `add_comment.cjs` (for content limits reference)

---

## Important Note: add-reaction and assign-issue

**add-reaction** and **assign-issue** are **NOT** agent safe-output types that process structured agent messages. The files you requested handle different flows:

| File | Purpose | Agent Safe-Output? |
|------|---------|-------------------|
| `add_reaction.cjs` | Activation job: adds a reaction when workflow is triggered (immediate feedback). Uses `GH_AW_REACTION` env var. | **No** |
| `assign_issue.cjs` | Activation job: assigns an issue to a user/agent when workflow runs. Uses `ASSIGNEE`, `ISSUE_NUMBER`, `GH_TOKEN` env vars. | **No** |

The documented safe-output types for similar behavior are:
- **Assign to User** (`assign-to-user`) – assigns users to issues (max: 1)
- **Assign to Agent** (`assign-to-agent`) – assigns Copilot agents (max: 1)

There is **no** `add-reaction` safe-output type in the gh-aw reference documentation.

---

## 1. add-labels Safe Output

**Handler:** `add_labels.cjs`

### Maximum body/content length
- **N/A** – labels do not have a body. Individual label strings are truncated to **64 characters** (GitHub API limit) during sanitization.

### Maximum number of labels allowed
- **Hard limit:** **10** labels per operation (`MAX_LABELS`).
- **Per-message config limit:** `config.max` (default: 10) caps how many labels pass validation; excess are sliced.
- Reference doc default: **max: 3** (configurable in workflow frontmatter).

### Content sanitization rules (labels)
- Labels starting with `-` are **rejected** (no label removal via this handler).
- Labels are **trimmed**, **deduplicated**.
- `sanitizeLabelContent`:
  - Unicode hardening (NFC normalization, decode HTML entities, strip zero-width chars, strip bidi controls, full-width → half-width).
  - Remove ANSI escape sequences.
  - Remove control characters (except newlines/tabs).
  - **Neutralize all @mentions** (wrap in backticks).
  - Remove characters: `<`, `>`, `&`, `'`, `"`.
- Each label truncated to 64 chars if longer.
- If `allowed` list is configured, only labels in that list are accepted.

### Rate limits / max counts
- **Per run:** `config.max` (default 10) – total labels added across all messages.
- **Per message:** 10 labels max (enforced before validation).
- If `allowed` is set and no labels match, returns "No valid labels found".

### Required fields
- **`labels`** – array, at least one valid label.
- **`item_number`** – optional; falls back to `context.payload.issue?.number` or `context.payload.pull_request?.number` if missing.
- **`repo`** – optional if `defaultTargetRepo` / `allowedRepos` configured.

### Other validation / restrictions
- Target repo must be in `allowedRepos` when that is configured.
- `item_number` must be a valid integer or resolvable from context.
- Staged mode: no API call; returns preview info only.

---

## 2. add-reaction (Activation Job – Not a Safe Output)

**File:** `add_reaction.cjs`  
**Used for:** Immediate reaction when workflow is triggered (activation), not agent output.

### Valid reaction types
- `+1`, `-1`, `laugh`, `confused`, `heart`, `hooray`, `rocket`, `eyes`
- Default: `eyes` (from `GH_AW_REACTION`)

### Supported event types
- `issues`, `issue_comment`, `pull_request`, `pull_request_review_comment`, `discussion`, `discussion_comment`

### Behavior
- Locks 403 errors with "locked" message are ignored (logged but not fatal).

---

## 3. assign-issue (Activation Job – Not a Safe Output)

**File:** `assign_issue.cjs`  
**Used for:** Assigning issues at activation time via env vars.

### Required environment variables
- **`GH_TOKEN`** – required for API calls.
- **`ASSIGNEE`** – required (trimmed).
- **`ISSUE_NUMBER`** – required (parsed as integer).

### Behavior
- Supports coding agents (e.g. Copilot): uses GraphQL API.
- For regular users: uses `gh issue edit --add-assignee`.
- Docs: https://github.github.com/gh-aw/reference/safe-outputs/#assigning-issues-to-copilot

---

## 4. close-issue Safe Output

**Handler:** `close_issue.cjs`

### Maximum body/content length
- **Default truncation:** 524,288 characters (512 KB) via `sanitizeContent`.
- **Line limit:** 65,000 lines; excess truncated with `[Content truncated due to line count]`.
- **Note:** add_comment enforces 65,536 chars (GitHub limit). close-issue relies on sanitization only; very long content may still hit GitHub API limits.

### Maximum number of mentions
- **No explicit mention limit** – mentions are **neutralized** (wrapped in backticks) by default.
- With `allowedAliases`, only listed aliases remain as real mentions; others are escaped.

### Content sanitization rules
All comment bodies pass through `sanitizeContent`:

1. **Unicode hardening:** NFC normalization, decode HTML entities, strip zero-width chars, bidi controls, full-width → half-width.
2. **Remove:** ANSI escape sequences, control chars (except `\n`, `\t`, `\r`).
3. **Neutralize:** leading `/command` (from `GH_AW_COMMAND`), all @mentions (unless in `allowedAliases`).
4. **Remove** XML comments.
5. **Convert** disallowed XML/HTML tags to parentheses; allow safe tags: b, blockquote, br, code, details, em, h1–h6, hr, i, li, ol, p, pre, strong, sub, summary, sup, table, tbody, td, th, thead, tr, ul.
6. **URL:** Non-https protocols redacted; domains filtered by `GH_AW_ALLOWED_DOMAINS` / GitHub context.
7. **Truncation:** 524,288 chars; 65,000 lines.
8. **GitHub refs:** Optional filtering via `GH_AW_ALLOWED_GITHUB_REFS`.
9. **Bot triggers:** "fixes #123", "closes #123", etc. wrapped in backticks.
10. **Template syntax:** `{{`, `<%=`, `${`, `{#`, `{%` escaped.
11. **Code regions:** Markdown fences balanced.

### Rate limits / max counts
- **Per run:** `config.max` (default: 10) close operations.

### Required fields
- **`body`** – required (or `config.comment` as fallback). Either message or config must provide non-empty comment.
- **`issue_number`** – optional; falls back to `context.payload?.issue?.number` when missing.
- **`repo`** – optional if `defaultTargetRepo` / `allowedRepos` configured.

### Other validation / restrictions
- **Required labels:** If `required_labels` is set, issue must have all of them.
- **Required title prefix:** If `required_title_prefix` is set, issue title must start with it.
- Comment is posted even when the issue is already closed.
- Target repo must be in `allowedRepos` when configured.
- Staged mode: no API calls; returns preview only.

---

## 5. close-pull-request Safe Output

**Handler:** `close_pull_request.cjs`

### Maximum body/content length
- Same as **close-issue**: default 524,288 chars, 65,000 lines via `sanitizeContent`.
- Final comment includes tracker ID and footer; total still limited by truncation.

### Maximum number of mentions
- Same as close-issue: mentions **neutralized** by default; no explicit limit.
- Optional filtering via `allowedAliases`.

### Content sanitization rules
- Same pipeline as close-issue (`sanitizeContent`).

### Rate limits / max counts
- **Per run:** `config.max` (default: 10).
- Reference doc: max 10.

### Required fields
- **`body`** – required (or `config.comment` as fallback).
- **`pull_request_number`** – optional; falls back to `context.payload?.pull_request?.number`.
- No repo override: always uses `context.repo` (same-repo only).

### Other validation / restrictions
- **Required labels:** If set, PR must have at least one of them (any match).
- **Required title prefix:** If set, PR title must start with it.
- Comment posted even when PR is already closed.
- Comment body includes tracker ID and footer (workflow name, run URL, etc.).
- Staged mode: no API calls; returns preview only.

---

## 6. link-sub-issue Safe Output

**Handler:** `link_sub_issue.cjs`

### Maximum body/content length
- **N/A** – no body/content; links two issues by number.

### Maximum number of mentions
- **N/A**.

### Content sanitization rules
- **N/A** – no user-provided text content.

### Rate limits / max counts
- **Per run:** `config.max` (default: **5**).
- Reference doc: max 1 (configurable).

### Required fields
- **`parent_issue_number`** – required; can be temporary ID (`aw_` + 3–8 alphanumeric).
- **`sub_issue_number`** – required; can be temporary ID.

### Other validation / restrictions
- **Same-repo only:** Parent and sub-issue must be in the same repository.
- **Temporary IDs:** Supports `aw_` prefixed IDs from create_issue; resolution deferred until resolved.
- **Parent filters:** If `parent_required_labels` or `parent_title_prefix` set, parent issue must satisfy them.
- **Sub-issue filters:** If `sub_required_labels` or `sub_title_prefix` set, sub-issue must satisfy them.
- **Existing parent:** Sub-issue may not already have a parent; attempt is rejected if it does.
- Staged mode: no API call; returns preview only.

---

## Shared Content Sanitization (close-issue, close-pull-request, add-comment)

When `sanitizeContent` is used (e.g. close-issue, close-pull-request, add-comment):

| Rule | Description |
|------|-------------|
| **Max length** | Default 524,288 chars (overridable via `maxLength`). add_comment enforces 65,536 before API. |
| **Max lines** | 65,000 lines |
| **Mentions** | Neutralized (backticks) unless in `allowedAliases`. add_comment: max 10 mentions. |
| **URLs** | Non-https and disallowed domains redacted |
| **Bot triggers** | "fixes #N", "closes #N" etc. wrapped in backticks |
| **Safe HTML** | b, blockquote, br, code, details, em, h1–h6, hr, i, li, ol, p, pre, strong, sub, summary, sup, table, tbody, td, th, thead, tr, ul allowed; others converted to parentheses |

### add-comment specific limits (for reference)
- **MAX_COMMENT_LENGTH:** 65,536 (GitHub limit)
- **MAX_MENTIONS:** 10
- **MAX_LINKS:** 50

---

## Environment variables affecting validation

| Variable | Purpose |
|----------|---------|
| `GH_AW_SAFE_OUTPUTS_STAGED` | `"true"` = staged mode; no API writes |
| `GH_AW_COMMAND` | Bot command name; leading `/command` neutralized |
| `GH_AW_ALLOWED_DOMAINS` | Comma-separated allowed URL domains |
| `GH_AW_ALLOWED_GITHUB_REFS` | Comma-separated allowed repo refs; empty = escape all |
| `GITHUB_SERVER_URL`, `GITHUB_API_URL` | Used for domain allowlist |

---

## Summary table

| Safe Output | Max items/run | Body limit | Mentions | Config max (default) |
|-------------|---------------|------------|-----------|----------------------|
| add-labels | config.max (10) | N/A (label: 64 chars) | Neutralized in labels | 10 labels/msg |
| add-reaction | N/A (activation) | N/A | N/A | N/A |
| assign-issue | N/A (activation) | N/A | N/A | N/A |
| close-issue | config.max (10) | 524,288 chars | Neutralized | - |
| close-pull-request | config.max (10) | 524,288 chars | Neutralized | - |
| link-sub-issue | config.max (5) | N/A | N/A | - |
