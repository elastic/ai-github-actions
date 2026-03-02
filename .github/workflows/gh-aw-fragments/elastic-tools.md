---
# Shared Elastic MCP servers — no `on:` field (shared component, not a runnable workflow)
# Each workflow defines its own tools (github, bash, web-fetch) and base network allows (defaults, github).
# This fragment provides only the Elastic-specific MCP servers and their network entries.
mcp-servers:
  public-code-search:
    url: "https://public-code-search.fastmcp.app/mcp"
    allowed: ["search_code"]
network:
  allowed:
    - "public-code-search.fastmcp.app"
    - "elastic.co"
    - "www.elastic.co"
    - "cloud.elastic.co"
    - "artifacts.elastic.co"
    - "ela.st"
---

## MCP Servers

- **`search_code`** — grep-style search across public GitHub repositories. Use for finding usage patterns in upstream libraries, reference implementations, or examples in open-source projects. This searches *public GitHub repos*, not the local codebase — if available you can use `grep` and file reading for local code.
