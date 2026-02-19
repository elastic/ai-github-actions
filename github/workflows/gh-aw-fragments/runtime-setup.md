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
    run: |
      set -euo pipefail
      install_dir="${{ github.workspace }}/.gh-aw-tools/bin"
      mkdir -p "$install_dir"
      cp "${{ steps.setup-uv.outputs.uv-path }}" "$install_dir/uv"
      chmod +x "$install_dir/uv"
      echo "$install_dir" >> "$GITHUB_PATH"
---
