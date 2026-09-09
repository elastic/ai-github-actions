## Workflow Editing Allowed

- This workflow **may** open pull requests that change files under `.github/` (including `.github/workflows/**`) when the fix is verified and necessary.
- Prefer an ephemeral / App token via `github-token-policy` so workflow-file pushes succeed. Classic `GITHUB_TOKEN` often cannot push workflow changes — that does **not** mean you should skip the PR when a capable token is configured.
- When a verified fix requires workflow YAML (or other `.github/`) changes: implement it, run validation, call `ready_to_make_pr`, then `create_pull_request`. Do **not** stop at `add_comment` alone for that case.
