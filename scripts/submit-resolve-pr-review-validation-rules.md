# submit-pull-request-review and resolve-pull-request-review-thread: Validation Rules

**Source:** [github/gh-aw](https://github.com/github/gh-aw) repository (main branch)

**Files analyzed:**
- `safe_outputs_tools.json` – tool definitions with schemas
- `pr_review_buffer.cjs` – PR review buffer handler (submit flow)
- `create_pr_review_comment.cjs` – inline comment handling and sanitization
- `sanitize_content.cjs`, `sanitize_content_core.cjs` – content sanitization
- Workflow lock files – validation config (field types, sanitize, maxLength)

---

## 1. submit-pull-request-review

### Description
Submit a pull request review with a status decision. All `create_pull_request_review_comment` outputs are collected and submitted as inline comments in this review. If the tool is not called, review comments are still submitted as a `COMMENT` review.

### Required fields
- **None** – all fields are optional in the schema.

### Optional fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `body` | string | `""` | Overall review summary in Markdown |
| `event` | string | `"COMMENT"` | Review decision (see enum below) |

### Event parameter options
- **`APPROVE`** – Approve the pull request
- **`REQUEST_CHANGES`** – Request changes before merging
- **`COMMENT`** – General feedback without a formal decision

### Validation rules

1. **`event`**
   - Must be one of: `APPROVE`, `REQUEST_CHANGES`, `COMMENT`
   - Default: `COMMENT` when omitted

2. **`body`**
   - **Semantic requirement:** Required when `event` is `REQUEST_CHANGES` (per tool description)
   - Optional for `APPROVE` and `COMMENT`
   - **maxLength:** 65,000 characters (workflow validation config)
   - **Sanitization:** Applied when `sanitize: true` in field config (see Content sanitization below)

3. **Rate limits**
   - **Per run:** `config.max` (default: 1) – maximum 1 review per workflow run
   - Configurable via `GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG` (e.g. `"submit_pull_request_review":{"max":1}`)

4. **Special behavior (from `pr_review_buffer.cjs`)**
   - **Own PRs:** If the reviewer is the PR author, `event` is forced to `COMMENT`. GitHub rejects `APPROVE` and `REQUEST_CHANGES` on your own PRs.
   - **Bot-authored PRs:** If the PR author is `github-actions[bot]`, only `COMMENT` is allowed; use the body to state the verdict.
   - **Footer:** A workflow footer may be appended to `body` based on `footer` config (`always`, `none`, `if-body`). With `if-body`, footer is added only when body is non-empty.

### Content sanitization (for `body`)

When `body` is provided and `sanitize: true`:

| Rule | Description |
|------|-------------|
| **Max length** | 65,000 characters (validation config overrides default 524,288) |
| **Max lines** | 65,000 lines (from `sanitizeContentCore`) |
| **Unicode hardening** | NFC normalization, HTML entity decode, strip zero-width chars, bidi controls, full-width→half-width |
| **Remove** | ANSI escape sequences, control chars (except `\n`, `\t`, `\r`) |
| **Neutralize** | Leading `/command`, all @mentions (wrap in backticks) |
| **Remove** | XML comments |
| **Convert** | Disallowed HTML tags to parentheses; allow: b, blockquote, br, code, details, em, h1–h6, hr, i, li, ol, p, pre, strong, sub, summary, sup, table, tbody, td, th, thead, tr, ul |
| **URLs** | Non-https protocols redacted; domains filtered by `GH_AW_ALLOWED_DOMAINS` / GitHub context |
| **Bot triggers** | "fixes #123", "closes #123", etc. wrapped in backticks |
| **Template syntax** | `{{`, `<%=`, `${`, `{#`, `{%` escaped |
| **Code regions** | Markdown fences balanced |

### Handler config options
- `footer`: `"always"` | `"none"` | `"if-body"` – controls when the workflow footer is appended to the review body
- `max`: 1 (typical) – max number of submit-review calls per run

---

## 2. resolve-pull-request-review-thread

### Description
Resolve a review thread on a pull request. Use after addressing feedback to mark a conversation as resolved. The `thread_id` must be the GraphQL node ID of the review thread (e.g. `PRRT_kwDO...`).

### Required fields
- **`thread_id`** (string) – The GraphQL node ID of the review thread to resolve (e.g. `PRRT_kwDOABCD...`). **Not** the numeric REST API comment ID.

### Validation rules

1. **`thread_id`**
   - **Type:** string
   - **Required:** yes
   - **Format:** GraphQL node ID (e.g. `PRRT_kwDO...`)
   - **No sanitization** – passed through to the GraphQL `resolveReviewThread` mutation

2. **Rate limits**
   - **Per run:** `config.max` (default: 10) – maximum 10 threads resolved per workflow run
   - Configurable via `GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG` (e.g. `"resolve_pull_request_review_thread":{"max":10}`)

3. **Additional properties**
   - **Not allowed** – `additionalProperties: false` in schema

### Content sanitization
- None – `thread_id` is an opaque GraphQL identifier and is not sanitized.

---

## Summary table

| Safe output | Required fields | Optional fields | Max/run | Body limits | Sanitization |
|-------------|-----------------|-----------------|---------|-------------|--------------|
| **submit-pull-request-review** | none | `body` (string), `event` (enum) | 1 | 65,000 chars | `body` sanitized |
| **resolve-pull-request-review-thread** | `thread_id` (string) | none | 10 | N/A | none |

---

## References
- [safe_outputs_tools.json](https://raw.githubusercontent.com/github/gh-aw/main/actions/setup/js/safe_outputs_tools.json)
- [pr_review_buffer.cjs](https://raw.githubusercontent.com/github/gh-aw/main/actions/setup/js/pr_review_buffer.cjs)
- [create_pr_review_comment.cjs](https://raw.githubusercontent.com/github/gh-aw/main/actions/setup/js/create_pr_review_comment.cjs)
- [sanitize_content.cjs](https://raw.githubusercontent.com/github/gh-aw/main/actions/setup/js/sanitize_content.cjs)
