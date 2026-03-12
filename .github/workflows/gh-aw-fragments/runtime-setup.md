---
steps:
  - name: Setup Go
    if: hashFiles(inputs['go-version-file'] || 'go.mod') != ''
    uses: actions/setup-go@v6
    with:
      go-version-file: ${{ inputs['go-version-file'] || 'go.mod' }}
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
      WORKSPACE: ${{ github.workspace }}
    run: |
      set -euo pipefail
      install_dir="$WORKSPACE/.gh-aw-tools/bin"
      mkdir -p "$install_dir"
      cp "$UV_PATH" "$install_dir/uv"
      chmod +x "$install_dir/uv"
      echo "$install_dir" >> "$GITHUB_PATH"
  
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
    env:
      GITHUB_REPOSITORY: ${{ github.repository }}
    run: |
      set -euo pipefail
      if [ -f "AGENTS.md" ]; then
        cp AGENTS.md /tmp/agents.md
        echo "Repository conventions copied from AGENTS.md to /tmp/agents.md"
      else
        OWNER="${GITHUB_REPOSITORY%/*}"
        REPO="${GITHUB_REPOSITORY#*/}"
        summary=$(curl -sf --max-time 15 -X POST https://agents-md-generator.fastmcp.app/mcp \
          -H "Content-Type: application/json" \
          -H "Accept: application/json, text/event-stream" \
          -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"generate_agents_md\",\"arguments\":{\"owner\":\"${OWNER}\",\"repo\":\"${REPO}\"}}}" \
          | sed 's/^data: //' \
          | jq -r '.result.structuredContent.summary // empty' 2>/dev/null) || true
        if [ -n "$summary" ]; then
          echo "$summary" > /tmp/agents.md
          echo "Repository conventions written to /tmp/agents.md"
        else
          echo "::warning::Could not fetch repository conventions; continuing without them"
        fi
      fi
---

Repository conventions are pre-fetched to `/tmp/agents.md`. Read this file early in your task to understand the codebase's conventions, guidelines, and patterns. If the file doesn't exist, continue without it. When spawning sub-agents, include the contents of `/tmp/agents.md` in each sub-agent's prompt (or tell the sub-agent to read the file directly).
