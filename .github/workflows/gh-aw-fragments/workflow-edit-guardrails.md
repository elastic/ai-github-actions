## Workflow Editing Guardrails

- Protected paths are enforced by safe outputs (for example, `.github/**` in PR create/push workflows).
- If a requested change touches a protected path, explain that the runtime blocked it and ask a maintainer to apply that change directly.
