---
# Shared Elastic AI configuration — no `on:` field (shared component, not a runnable workflow)
# Note: engine/model must be set in the shim (not importable)
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash: true
  web-fetch:
mcp-servers:
  agents-md-generator:
    url: "https://agents-md-generator.fastmcp.app/mcp"
    allowed: ["generate_agents_md"]
  public-code-search:
    url: "https://public-code-search.fastmcp.app/mcp"
    allowed: ["search_code"]
network:
  allowed:
    - defaults
    - github
    - "agents-md-generator.fastmcp.app"
    - "public-code-search.fastmcp.app"
---

## MCP Servers

- **`generate_agents_md`** — generates a summary of the repository's structure, conventions, and coding guidelines from AGENTS.md and related files. Call at the start of every workflow to get repo context.
- **`search_code`** — grep-style search across public GitHub repositories. Use for finding usage patterns in upstream libraries, reference implementations, or examples in open-source projects. This searches *public GitHub repos*, not the local codebase — if available you can use `grep` and file reading for local code.
