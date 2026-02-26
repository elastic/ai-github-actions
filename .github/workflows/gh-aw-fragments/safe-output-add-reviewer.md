---
safe-outputs:
  add-reviewer:
    max: 3
---

## add-reviewer Limitations

- **Max reviewers per run**: 3 (configurable with `max`).
- **Pull requests only**: Reviewers can only be added to pull requests, not issues.
- **Target**: `"triggering"` (default, requires PR event), `"*"` (any PR), or a specific PR number.
- **Requires PR number**: When `target: "*"`, the agent must provide `pull_request_number` in its output to identify which PR to assign.
- **Username validation**: Usernames are validated; invalid or non-existent users are rejected.
