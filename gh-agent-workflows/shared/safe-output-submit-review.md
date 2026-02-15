---
safe-outputs:
  submit-pull-request-review:
    max: 1
    footer: "if-body"
---

## submit-pull-request-review Limitations

- **Event**: Must be one of `APPROVE`, `REQUEST_CHANGES`, or `COMMENT`. Defaults to `COMMENT` if omitted.
- **Body**: Max 65,000 characters. Required when event is `REQUEST_CHANGES`. Sanitized (mentions neutralized, HTML filtered, URLs restricted).
- **Own PRs**: If the workflow actor is also the PR author (e.g., `github-actions[bot]` reviewing its own PR), the event is forced to `COMMENT` regardless of what you specify. `APPROVE` and `REQUEST_CHANGES` will not work.
- **Max per run**: 1 review submission per workflow run. Leave inline comments first, then submit the review as a single final action.
