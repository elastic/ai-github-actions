---
steps:
  - name: Setup Go
    if: hashFiles('**/go.mod') != ''
    uses: actions/setup-go@v5
    with:
      go-version-file: go.mod
      cache: true

  - name: Setup Python
    if: hashFiles('**/.python-version') != ''
    uses: actions/setup-python@v5
    with:
      python-version-file: '.python-version'

  - name: Setup Node.js
    if: hashFiles('**/package.json') != ''
    uses: actions/setup-node@v6
    with:
      node-version-file: 'package.json'

  - name: Setup Ruby
    if: hashFiles('**/.ruby-version') != ''
    uses: ruby/setup-ruby@v1
    with:
      ruby-version: '.ruby-version'
      bundler-cache: true

  - name: Setup uv
    if: hashFiles('**/pyproject.toml', '**/uv.lock') != ''
    uses: astral-sh/setup-uv@v5
---
