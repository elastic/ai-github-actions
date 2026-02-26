---
safe-outputs:
  assign-to-user:
    max: 1
---

## assign-to-user Limitations

- **Max assignments per run**: 1 by default (configurable with `max`).
- **Target**: `"triggering"` (default, requires issue event), `"*"` (any issue), or a specific issue number.
- **Requires issue number**: When `target: "*"`, the agent must provide `issue_number` in its output to identify which issue to assign.
- **Username validation**: Usernames are validated; invalid or non-existent users are rejected.
