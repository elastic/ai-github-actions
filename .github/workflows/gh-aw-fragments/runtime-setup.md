---
steps:
  - name: Setup Go
    if: hashFiles('go.mod') != ''
    uses: actions/setup-go@v5
    with:
      go-version-file: go.mod
      cache: true

  - name: Setup Python
    if: hashFiles('.python-version') != ''
    uses: actions/setup-python@v5
    with:
      python-version-file: '.python-version'

  - name: Setup Node.js (.node-version)
    if: hashFiles('.node-version') != ''
    uses: actions/setup-node@v6
    with:
      node-version-file: '.node-version'

  - name: Setup Node.js (.nvmrc)
    if: hashFiles('.node-version') == '' && hashFiles('.nvmrc') != ''
    uses: actions/setup-node@v6
    with:
      node-version-file: '.nvmrc'

  - name: Setup Ruby
    if: hashFiles('.ruby-version') != ''
    uses: ruby/setup-ruby@v1
    with:
      ruby-version: '.ruby-version'
      bundler-cache: true

  - name: Setup uv
    if: hashFiles('pyproject.toml', 'uv.lock') != ''
    uses: astral-sh/setup-uv@v5
    id: setup-uv

  - name: Expose uv in workspace
    if: hashFiles('pyproject.toml', 'uv.lock') != ''
    shell: bash
    env:
      UV_PATH: ${{ steps.setup-uv.outputs.uv-path }}
    run: |
      set -euo pipefail
      # AWF-friendly location: gh-aw scans /opt/hostedtoolcache/**/bin paths.
      toolcache_bin="/opt/hostedtoolcache/gh-aw-tools/current/x64/bin"
      uv_bin="${UV_PATH:-$(command -v uv || true)}"
      if [ -z "$uv_bin" ]; then
        echo "::error::uv was not installed or not discoverable after setup-uv" >&2
        exit 1
      fi
      sudo mkdir -p "$toolcache_bin"
      sudo ln -sf "$uv_bin" "$toolcache_bin/uv"
  
  - name: Configure Copilot CLI settings
    shell: bash
    run: |
      set -euo pipefail
      mkdir -p ~/.copilot
      CONFIG="$HOME/.copilot/config.json"
      if [ -f "$CONFIG" ]; then
          jq '. + {"chat.customAgentInSubagent.enabled": true}' "$CONFIG" > "$CONFIG.tmp" && mv "$CONFIG.tmp" "$CONFIG"
      else
          echo '{"chat.customAgentInSubagent.enabled":true}' > "$CONFIG"
      fi

  - name: Fetch repository conventions
    shell: bash
    run: |
      set -euo pipefail
      if [ -f "AGENTS.md" ]; then
        cp AGENTS.md /tmp/agents.md
        echo "Repository conventions copied from AGENTS.md to /tmp/agents.md"
      else
        echo "No AGENTS.md found; continuing without repository conventions"
      fi
---

Repository conventions are pre-fetched to `/tmp/agents.md`. Read this file early in your task to understand the codebase's conventions, guidelines, and patterns. If the file doesn't exist, continue without it. When spawning sub-agents, include the contents of `/tmp/agents.md` in each sub-agent's prompt (or tell the sub-agent to read the file directly).
