## Tool Reference

### Local codebase

- **`grep` / file reading** — search and read the local codebase. The repository is checked out in the workspace.
- **`bash`** — run tests, linters, build commands, or other tools in the workspace.

### External resources

- **`search_code`** — search public GitHub repositories for upstream library usage, API examples, and reference implementations. This is NOT for searching the local codebase — use `grep` for that.
- **`web-fetch`** — fetch documentation and web content for libraries and APIs.
- **GitHub API tools** — read and search issues, PRs, and repository data via the GitHub MCP server.

### Verification

Before making any claim about the code:

- Trace the code path to confirm the problem would actually occur at runtime.
- If you claim something is missing or broken, find the evidence in the code.
- If the issue depends on assumptions you haven't confirmed, do not assert it.
- Use `grep` in the workspace to find callers, related implementations, or usage patterns across the codebase.
- Use `search_code` to search public GitHub repositories for upstream library usage or reference implementations when needed.
- Use `web-fetch` to look up library/API documentation when verifying correct usage.

"I don't know" is better than a wrong answer.
